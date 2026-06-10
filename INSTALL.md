# Installation Instructions

This guide covers the recommended setup for the Digitransit custom integration.

## Prerequisites

- Home Assistant 2023.10.0 or newer
- Digitransit API subscription key (https://digitransit.fi)
- Bus stop IDs (for example `HSL:1010105`, `Vaasa:159712`)

## Install via HACS (Recommended)

1. Open HACS in Home Assistant.
2. Add this repository as a custom repository if needed.
3. Install Digitransit integration.
4. Restart Home Assistant.

## Manual Install

1. Copy `custom_components/digitransit` into your Home Assistant config at:

	`/config/custom_components/digitransit`

2. Restart Home Assistant.

## Configure in Home Assistant UI

1. Go to Settings -> Devices & Services.
2. Click Add Integration.
3. Search for Digitransit.
4. Enter API key.
5. Add stop IDs and select router for each stop.

## Finding Stop IDs

- HSL region: https://reittiopas.hsl.fi
- Waltti/city planners: city-specific Digitransit sites (for example `tampere.digitransit.fi`)

## Verification

1. Open Developer Tools -> States.
2. Search for `sensor.` entities created by Digitransit.
3. Confirm sensor attributes include `departures` and next departure details.

## Legacy YAML Mode (Optional)

Legacy YAML files are still available as examples in repository root:

- `sensor_config.yaml`
- `sensor_config.example.yaml`
- `template_sensors.yaml`
- `lovelace_card.yaml`

These are not required for the config-flow custom integration setup.
