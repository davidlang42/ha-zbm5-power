# ZBM5 Power and Energy Calculator for Home Assistant

A custom Home Assistant integration that calculates precise live power (Watts) and cumulative energy consumption (kWh) for **ZBM5 light switches**. It accounts for custom configurations like number of gangs, wiring type (neutral vs. no neutral), relay modes (normal vs. detached), and individual light bulb wattages—all configurable and editable directly through the Home Assistant UI.

## Features

- **UI Configurable & Options Flow:** Set up your devices and update bulb wattages or relay modes on the fly via **Settings > Devices & Services** without touching YAML.
- **Dynamic Power Calculation ($W$):** Automatically factors in switch base power consumption, relay states, and custom bulb wattages.
- **Built-in Energy Tracking ($kWh$):** Natively creates both a Power sensor and an Energy integration sensor simultaneously with zero extra helper setup required.
- **Energy Dashboard Ready:** The generated energy sensors are fully compatible with Home Assistant's built-in Energy Dashboard under *Individual Devices*.

---

## Installation

### Method 1: HACS (Recommended)
1. Ensure you have [HACS](https://hacs.xyz/) installed.
2. Open HACS in Home Assistant.
3. Click the three dots in the top right corner and select **Custom repositories**.
4. Paste your GitHub repository URL, select category **Integration**, and click **Add**.
5. Search for **ZBM5 Power & Energy Calculator** in HACS, click **Download**, and restart Home Assistant.

### Method 2: Manual Installation
1. Download or copy the `zbm5_power` folder from `custom_components/` into your Home Assistant `config/custom_components/` directory.
2. Restart Home Assistant.

---

## Configuration & Usage

1. Go to **Settings** > **Devices & Services** > **Add Integration**.
2. Search for **ZBM5 Power Calculator** and select it.
3. Fill out the configuration form:
   - **Name:** Friendly name for your switch (e.g., *Living Room Lights*).
   - **Light Entity:** The target light entity controlled by this switch.
   - **Number of Gangs:** Select 1, 2, or 3 gangs.
   - **Wiring Type:** Choose *No Neutral* ($0.05\text{W}$ base) or *With Neutral* ($0.15\text{W}$ base).
   - **Relay Mode:** Choose *Normal* (relay active only when light is on) or *Detached* (relay always active).
   - **Bulb Wattage:** The power draw of your installed light bulb in Watts.

### Updating Settings (e.g., Changing Bulbs)
When you change a light bulb or modify your switch configuration:
1. Navigate to **Settings** > **Devices & Services**.
2. Find your ZBM5 device and click **Configure**.
3. Update your bulb wattage or settings directly in the popup UI—the sensors will update instantly.