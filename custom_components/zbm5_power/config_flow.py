import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

class ZBM5PowerConfigFlow(config_entries.ConfigFlow, domain="zbm5_power"):
    """Handle a config flow for ZBM5 Power."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial setup step via UI."""
        errors = {}
        if user_input is not None:
            return self.async_create_entry(title=user_input.get("name", "ZBM5 Switch"), data=user_input)

        schema = vol.Schema({
            vol.Required("name", default="ZBM5 Light"): str,
            vol.Required("light_entity"): selector.EntitySelector(selector.EntitySelectorConfig(domain="light")),
            vol.Required("gangs", default="1"): selector.SelectSelector(selector.SelectSelectorConfig(options=["1", "2", "3"], mode="dropdown")),
            vol.Required("wiring_type", default="no_neutral"): selector.SelectSelector(selector.SelectSelectorConfig(options=[{"label": "No Neutral", "value": "no_neutral"}, {"label": "With Neutral", "value": "with_neutral"}], mode="dropdown")),
            vol.Required("relay_mode", default="normal"): selector.SelectSelector(selector.SelectSelectorConfig(options=[{"label": "Normal", "value": "normal"}, {"label": "Detached", "value": "detached"}], mode="dropdown")),
            vol.Required("bulb_wattage", default=10.0): selector.NumberSelector(selector.NumberSelectorConfig(min=0, max=200, step=0.1, unit_of_measurement="W")),
        })

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return ZBM5PowerOptionsFlowHandler(config_entry)

class ZBM5PowerOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow to edit values later from the UI."""

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current = self.config_entry.options if self.config_entry.options else self.config_entry.data

        schema = vol.Schema({
            vol.Required("gangs", default=current.get("gangs", "1")): selector.SelectSelector(selector.SelectSelectorConfig(options=["1", "2", "3"], mode="dropdown")),
            vol.Required("wiring_type", default=current.get("wiring_type", "no_neutral")): selector.SelectSelector(selector.SelectSelectorConfig(options=[{"label": "No Neutral", "value": "no_neutral"}, {"label": "With Neutral", "value": "with_neutral"}], mode="dropdown")),
            vol.Required("relay_mode", default=current.get("relay_mode", "normal")): selector.SelectSelector(selector.SelectSelectorConfig(options=[{"label": "Normal", "value": "normal"}, {"label": "Detached", "value": "detached"}], mode="dropdown")),
            vol.Required("bulb_wattage", default=current.get("bulb_wattage", 10.0)): selector.NumberSelector(selector.NumberSelectorConfig(min=0, max=200, step=0.1, unit_of_measurement="W")),
        })

        return self.async_show_form(step_id="init", data_schema=schema)