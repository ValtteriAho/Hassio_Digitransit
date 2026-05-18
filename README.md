# 🚌 Digitransit Bus Timetables for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://hacs.xyz)
[![License](https://img.shields.io/github/license/valtteri-aho/Hassio-digitransit.svg)](LICENSE)

Display real-time Finnish bus schedules from Digitransit API in your Home Assistant dashboard using YAML-based configuration.

## 📋 What's Included

- `sensor_config.yaml` - REST sensors to fetch data from Digitransit API
- `sensor_config.example.yaml` - Template configuration file with placeholders
- `template_sensors.yaml` - Template sensors to format the data
- `lovelace_card.yaml` - 4 dashboard card options

## 🎯 Features

- ✅ **Real-time departures** - Live GPS-tracked bus locations and times
- ✅ **Delay indicators** - Visual indicator (🔴) when real-time data is available
- ✅ **Up to 5 departures** per stop (configurable)
- ✅ **Multiple stops** - Monitor 2 or more bus stops simultaneously
- ✅ **Auto-refresh** - Updates every 60 seconds (configurable)
- ✅ **Minutes to departure** - Shows countdown until bus leaves
- ✅ **All Finnish cities** - Works with any Digitransit-powered region
- ✅ **Flexible display** - 4 pre-built Lovelace card options

## 🇫🇮 Supported Cities

Works with Finnish cities/regions that use Digitransit.

| Region | Router | Example Stop Code |
|--------|--------|------------------|
| **Helsinki (HSL)** | `hsl` | `HSL:1010105` |
| **Tampere** | `waltti` | `tampere:0001` |
| **Turku (FOLI)** | `waltti` | `FOLI:1` |
| **Oulu** | `waltti` | `oulu:1001` |
| **Vaasa** | `waltti` | `Vaasa:159712` |
| **Jyväskylä** | `waltti` | `jyvaskyla:1001` |
| **Kuopio** | `waltti` | `kuopio:1001` |
| **Lahti** | `waltti` | `lahti:1001` |
| **Lappeenranta** | `waltti` | `lappeenranta:1` |
| **Other cities** | `waltti` or `finland` | Varies |

## 📦 Requirements

- **Home Assistant** 2023.1.0 or newer
- **Digitransit API key** (free registration at [digitransit.fi](https://digitransit.fi))
- Built-in integrations: REST, Template

## ⚡ Quick Start

### 1) Get API key

1. Visit [digitransit.fi](https://digitransit.fi)
2. Register and create a subscription key
3. Save your key

### 2) Find stop codes

- Helsinki (HSL): [reittiopas.hsl.fi](https://reittiopas.hsl.fi)
- Other cities: city-specific Digitransit site (for example `tampere.digitransit.fi`)

Stop codes look like `HSL:1010105` or `Vaasa:159712`.

### 3) Configure Home Assistant

Add to `configuration.yaml`:

```yaml
rest: !include bussiaikataulu/sensor_config.yaml
template: !include bussiaikataulu/template_sensors.yaml
```

In `sensor_config.yaml`, replace:
- `YOUR_API_KEY`
- `ROUTER` (`hsl`, `waltti`, or `finland`)
- `CITY:STOPCODE`

### 4) Restart Home Assistant

- Settings → System → Restart

### 5) Add dashboard card

- Use one of the examples from `lovelace_card.yaml`

## 📊 Available Sensors

### Raw data sensors
- `sensor.bussi_pysakki_1_raw`
- `sensor.bussi_pysakki_2_raw`

### Formatted sensors
- `sensor.bussiaikataulu_pysakki_1`
- `sensor.bussiaikataulu_pysakki_2`
- `sensor.bussiaikataulu_yhdistetty`

Formatted output pattern:

`[Route] → [Destination] | [Time] ([Minutes] min) [🔴 if real-time]`

## 🔧 Troubleshooting

### Sensors not appearing

1. Verify `configuration.yaml` includes:
   ```yaml
   rest: !include bussiaikataulu/sensor_config.yaml
   template: !include bussiaikataulu/template_sensors.yaml
   ```
2. Restart Home Assistant
3. Check logs in Settings → System → Logs

### No departures

1. Verify stop code format and value
2. Verify router in API URL
3. Verify API key header value

## 📄 Documentation

- Installation details: `INSTALL.md`
- Changelog: `CHANGELOG.md`
- HACS/repository info: `info.md`

## 🐛 Support

- Report issues: `https://github.com/valtteri-aho/Hassio-digitransit/issues`
- Home Assistant community: `https://community.home-assistant.io/`
