# Digitransit for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://hacs.xyz)
[![License](https://img.shields.io/github/license/valtteri-aho/Hassio-digitransit.svg)](LICENSE)

Real-time Finnish public transit departures in Home Assistant via Digitransit GraphQL API.

## Release

- Current release: `0.1.5`
- This is the first public release of the integration.

## Features

- Config flow setup from Home Assistant UI
- Multiple stops per integration entry
- Configurable number of departures per stop
- Real-time delay information in attributes
- 60 second polling interval
- Works across Digitransit-powered Finnish regions

## Requirements

- Home Assistant 2023.10.0 or newer
- Digitransit API subscription key from https://portal-api.digitransit.fi/

## Quick Start (Recommended)

1. Install this integration into your Home Assistant `custom_components` directory (or via HACS).
2. Restart Home Assistant.
3. Go to Settings -> Devices & Services -> Add Integration.
4. Search for Digitransit.
5. Enter your Digitransit API subscription key.
6. Add one or more stop IDs (for example `HSL:1010105` or `Vaasa:159712`) and choose the matching router.

## Install via HACS Custom Repository

1. Open HACS in Home Assistant.
2. Go to Integrations.
3. Open the menu and select Custom repositories.
4. Add repository URL: `https://github.com/ValtteriAho/Hassio_Digitransit`
5. Category: `Integration`
6. Install `Digitransit` from HACS and restart Home Assistant.

## Stop IDs and Routers

You can find stop IDs from your city route planner:

- HSL: https://reittiopas.hsl.fi
- Waltti cities: city-specific Digitransit instances (for example `tampere.digitransit.fi`)

The stop ID must belong to the router you select in the integration. An HSL stop ID must use the `hsl` router. Waltti stop IDs must include the city/feed prefix with the correct capitalization, for example `Vaasa:159712` (not `vaasa:159712`), and use the `waltti` router.

Router choices in the integration:

- `waltti`
- `hsl`
- `tampere`
- `turku`
- `jyvaskyla`
- `oulu`
- `lahti`

## Entity Output

Each configured stop creates one sensor entity.

- Sensor state: minutes until next departure (`Now`, `1 min`, `N min`)
- Sensor attributes: departure list with route, destination, scheduled time, realtime flag, and delay

## Legacy YAML Examples

This repository still includes legacy YAML examples:

- `sensor_config.yaml`
- `sensor_config.example.yaml`
- `template_sensors.yaml`
- `lovelace_card.yaml`

These are examples only. The maintained setup path is the config-flow custom integration.

## Troubleshooting

If entities do not appear:

1. Confirm the integration is loaded under Settings -> Devices & Services.
2. Confirm subscription key is valid and active in Digitransit API portal.
3. Confirm stop IDs exist in Digitransit.
4. Check logs under Settings -> System -> Logs.

## Documentation

- Installation details: `INSTALL.md`
- Changelog: `CHANGELOG.md`
- Repository info: `info.md`

## Support

- Issues: https://github.com/valtteri-aho/Hassio-digitransit/issues
- Home Assistant Community: https://community.home-assistant.io/
