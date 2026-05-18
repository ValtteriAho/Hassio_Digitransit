# Installation Instructions

Quick guide for adding Digitransit Bus Timetables to your Home Assistant.

## Prerequisites

✅ Home Assistant 2023.1.0 or newer  
✅ Digitransit API subscription key ([Get one here](https://digitransit.fi))  
✅ Your bus stop codes

## Installation Steps

### 1. Download Files

Clone or download this repository to your Home Assistant config directory:

```bash
cd /config
git clone https://github.com/valtteri-aho/Hassio-digitransit.git bussiaikataulu
```

Or manually download and extract to `/config/bussiaikataulu/`

### 2. Configure Your Stops

Copy the example file and edit it:

```bash
cd bussiaikataulu
cp sensor_config.example.yaml sensor_config.yaml
nano sensor_config.yaml
```

Replace these placeholders:
- `YOUR_API_KEY` → Your Digitransit subscription key
- `ROUTER` → `hsl` (Helsinki) or `waltti` (other cities)
- `CITY:STOPCODE` → Your actual stop codes (e.g., `Vaasa:159712`)

### 3. Add to configuration.yaml

Add these lines to your `/config/configuration.yaml`:

```yaml
rest: !include bussiaikataulu/sensor_config.yaml
template: !include bussiaikataulu/template_sensors.yaml
```

### 4. Restart Home Assistant

Settings → System → Restart

### 5. Add Dashboard Card

1. Edit your dashboard
2. Add card → Manual (YAML)
3. Copy one of the card configs from `lovelace_card.yaml`
4. Save

## Finding Your Stop Codes

**Helsinki region:**
- Go to [reittiopas.hsl.fi](https://reittiopas.hsl.fi)
- Search for your stop
- Code is in URL: `HSL:1010105`

**Other cities:**
- Visit your city's site (e.g., `tampere.digitransit.fi`)
- Click your stop
- Code is in URL: `CityName:XXXXX`

## Verification

Check that sensors appear:
- Developer Tools → States
- Search for: `bussi_pysakki`
- Should see 5 new sensors

## Need Help?

See [README.md](README.md) for detailed troubleshooting.
