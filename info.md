# Digitransit for Home Assistant

Home Assistant custom integration for real-time Finnish public transit departures from Digitransit API.

## Highlights

- Config-flow setup from Home Assistant UI
- Multiple stops per integration entry
- Configurable departure count
- Real-time delay and departure attributes
- 60 second polling

## Requirements

- Home Assistant 2023.10.0+
- Digitransit API subscription key from https://portal-api.digitransit.fi/

## Included Files

- `custom_components/digitransit/` custom integration source
- `lovelace_card.yaml` example dashboard cards
- `sensor_config.yaml`, `sensor_config.example.yaml`, `template_sensors.yaml` legacy YAML examples

## Setup

1. Install integration via HACS or copy `custom_components/digitransit` to Home Assistant config directory.
2. Restart Home Assistant.
3. Add integration from Settings -> Devices & Services.
4. Enter Digitransit API subscription key and configure stop IDs.

## Support

- Documentation: https://github.com/valtteri-aho/Hassio-digitransit
- Issues: https://github.com/valtteri-aho/Hassio-digitransit/issues
- Community: https://community.home-assistant.io/
