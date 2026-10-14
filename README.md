# Digitransit for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://hacs.xyz)
[![License](https://img.shields.io/github/license/valtteri-aho/Hassio-digitransit.svg)](LICENSE)

Real-time Finnish public transit departures in Home Assistant via Digitransit GraphQL API.

## Release

- Current release: `0.2.0`

## Features

- **Config Flow & Options Flow**: Easy setup from Home Assistant UI; add or remove stops and tweak settings without reinstalling
- **Concurrent API Updates**: Polling multiple stops concurrently via `asyncio.gather` for minimal latency
- **Configurable Update Interval**: Flexible 15–300 second polling frequency
- **Route Filtering**: Filter departures per stop to show only the lines you care about
- **Native Timestamp Sensor**: `SensorDeviceClass.TIMESTAMP` sensor providing dynamic live Lovelace countdowns ("in 5 minutes")
- **Real-Time Delays & Status**: Detailed status indicators (On time, Late, Early, Scheduled) and Lovelace color tags
- **Diagnostics**: Built-in Home Assistant diagnostics support with API key redaction
- **Multi-Region Support**: Covers HSL, Waltti cities, and nationwide transit (VR trains, Matkahuolto)

## Requirements

- Home Assistant 2023.10.0 or newer
- Digitransit API subscription key from https://portal-api.digitransit.fi/

## Quick Start (Recommended)

1. Install this integration into your Home Assistant `custom_components` directory (or via HACS).
2. Restart Home Assistant.
3. Go to Settings -> Devices & Services -> Add Integration.
4. Search for **Digitransit**.
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

- Finland (Nationwide / Trains / Regional): https://opas.matka.fi
- HSL: https://reittiopas.hsl.fi
- Waltti cities: city-specific Digitransit instances (for example `tampere.digitransit.fi`)

Router choices in the integration:

- `finland` (Nationwide: trains, long-distance buses, regional)
- `waltti` (All Waltti cities: Vaasa, Hämeenlinna, Joensuu, etc.)
- `hsl` (Helsinki region)
- `varely` (Varsinais-Suomi / Southwest Finland)
- `tampere`
- `turku`
- `jyvaskyla`
- `oulu`
- `lahti`

## Entity Output

Each configured stop creates three sensor entities grouped under the stop device:

1. **Next departure** (`sensor.<stop_name>_next_departure`):
   - State: minutes until next departure (`Now`, `1 min`, `N min`)
   - Attributes: full departure list (`departures`), individual departures (`lahto_1`, `lahto_2`), scheduled vs estimated times, delay, and status
   - Dynamic icon and status colors (`status_icon`, `status_color`)
2. **Next departure time** (`sensor.<stop_name>_next_departure_time`):
   - Device class: `timestamp`
   - Native UTC ISO-8601 timestamp allowing Lovelace UI to render live countdowns
3. **Next 3 departures** (`sensor.<stop_name>_next_3_departures`):
   - State format: `HH:MM | HH:MM | HH:MM` for a quick glance

## Options Flow

Once installed, navigate to **Settings -> Devices & Services -> Digitransit -> Configure** to:
- **Add New Stop**: Add additional stops at any time
- **Remove Stop**: Select and remove unwanted stops
- **General Settings**: Adjust default departures and update interval (15-300 seconds)

## Troubleshooting

If entities do not appear:

1. Confirm the integration is loaded under Settings -> Devices & Services.
2. Confirm subscription key is valid and active in Digitransit API portal.
3. Confirm stop IDs exist in Digitransit.
4. Download diagnostics under integration device page to inspect API responses.
5. Check logs under Settings -> System -> Logs.

## Documentation

- Installation details: `INSTALL.md`
- Changelog: `CHANGELOG.md`
- Repository info: `info.md`
- Lovelace examples: `lovelace_card.yaml`

## Support

- Issues: https://github.com/valtteri-aho/Hassio-digitransit/issues
- Home Assistant Community: https://community.home-assistant.io/
