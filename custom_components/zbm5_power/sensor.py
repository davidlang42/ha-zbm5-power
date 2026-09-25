"""Sensor platform for ZBM5 Power and Energy."""
from datetime import timedelta
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.components.integration.sensor import IntegrationSensor
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er, device_registry as dr
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the ZBM5 power and energy sensors from a config entry."""
    data = entry.options if entry.options else entry.data
    light_entity_id = data.get("light_entity")
    device_name = data.get("name", "ZBM5")

    # Look up the light's device registry entry so we can share its device info
    light_device_id = None
    if light_entity_id:
        ent_reg = er.async_get(hass)
        if light_entry := ent_reg.async_get(light_entity_id):
            light_device_id = light_entry.device_id

    # Look up the power entity ID dynamically from the Entity Registry
    ent_reg = er.async_get(hass)
    power_unique_id = f"{entry.entry_id}_power"
    power_entity_id = ent_reg.async_get_entity_id("sensor", entry.domain, power_unique_id)

    # Fallback for the very first boot before the entity registry registers it
    if not power_entity_id:
        slug_name = "".join(c if c.isalnum() else "_" for c in device_name.lower()).strip("_")
        power_entity_id = f"sensor.{slug_name}_power"

    power_sensor = Zbm5PowerSensor(entry, light_device_id)
    
    energy_sensor = IntegrationSensor(
        integration_method="trapezoidal",
        name=f"{device_name} Energy",
        unique_id=f"{entry.entry_id}_energy",
        source_entity=power_entity_id,
        unit_prefix="k",
        unit_time="h",
        round_digits=3,
        max_sub_interval=None,
    )

    # If we found a parent device for the light, link the energy sensor to it too
    if light_device_id:
        dev_reg = dr.async_get(hass)
        if dev_entry := dev_reg.async_get(light_device_id):
            energy_sensor._attr_device_info = {
                "identifiers": dev_entry.identifiers,
                "connections": dev_entry.connections,
                "name": dev_entry.name,
                "manufacturer": dev_entry.manufacturer,
                "model": dev_entry.model,
            }

    async_add_entities([power_sensor, energy_sensor])

class Zbm5PowerSensor(SensorEntity):
    """Representation of a ZBM5 Power Sensor."""

    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "W"

    def __init__(self, entry: ConfigEntry, light_device_id: str | None) -> None:
        """Initialize the sensor."""
        self._entry = entry
        self._light_device_id = light_device_id
        self._attr_name = f"{entry.data.get('name', 'ZBM5')} Power"
        self._attr_unique_id = f"{entry.entry_id}_power"
        self._unsub_watcher = None
        self._update_config()

    @property
    def device_info(self):
        """Return device information to tie this sensor to the target light's device."""
        if self._light_device_id:
            # Look up the light's device identifiers so we nest cleanly under it
            dev_reg = dr.async_get(self.hass)
            if dev_entry := dev_reg.async_get(self._light_device_id):
                return {
                    "identifiers": dev_entry.identifiers,
                    "connections": dev_entry.connections,
                    "name": dev_entry.name,
                    "manufacturer": dev_entry.manufacturer,
                    "model": dev_entry.model,
                }

        # Fallback to standard config entry device info if light has no device
        return {
            "identifiers": {(self._entry.domain, self._entry.entry_id)},
            "name": self._entry.data.get("name", "ZBM5 Power"),
            "manufacturer": "Custom Integration",
        }

    @callback
    def _update_config(self) -> None:
        """Fetch latest configuration or options."""
        data = self._entry.options if self._entry.options else self._entry.data
        self._light_entity = data.get("light_entity") or self._entry.data.get("light_entity")
        self._gangs = int(data.get("gangs", 1))
        self._wiring_type = data.get("wiring_type", "no_neutral")
        self._relay_mode = data.get("relay_mode", "normal")
        self._bulb_wattage = float(data.get("bulb_wattage", 10.0))

        # Re-bind state watchers if already added to hass
        if self.hass:
            self._async_setup_watcher()

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added to hass."""
        await super().async_added_to_hass()
        # Listen for options changes
        self.async_on_remove(self._entry.add_update_listener(self._async_update_listener))
        self._async_setup_watcher()

    @callback
    def _async_setup_watcher(self) -> None:
        """Set up state change listeners for the target light entity."""
        if self._unsub_watcher:
            self._unsub_watcher()
            self._unsub_watcher = None

        if self._light_entity:
            @callback
            def _state_changed_listener(event):
                self.async_write_ha_state()

            self._unsub_watcher = async_track_state_change_event(
                self.hass, [self._light_entity], _state_changed_listener
            )

    async def _async_update_listener(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Handle options update from UI."""
        self._update_config()
        self.async_write_ha_state()

    @property
    def native_value(self):
        """Return the calculated power state."""
        light_state = self.hass.states.get(self._light_entity) if self._light_entity else None
        is_on = light_state and light_state.state == "on"

        # Switch Power
        switch_p = (0.05 if self._wiring_type == 'no_neutral' else 0.15) / self._gangs

        # Relay Power
        if self._relay_mode == 'detached':
            relay_p = 0.2
        else:
            relay_p = 0.2 if is_on else 0.0

        # Light Power
        light_p = self._bulb_wattage if is_on else 0.0

        return round(switch_p + relay_p + light_p, 3)

    @property
    def extra_state_attributes(self):
        """Return device state attributes for debugging/reference."""
        return {
            "light_entity": self._light_entity,
            "gangs": self._gangs,
            "wiring_type": self._wiring_type,
            "relay_mode": self._relay_mode,
            "bulb_wattage": self._bulb_wattage,
        }