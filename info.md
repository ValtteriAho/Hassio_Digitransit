# 🚌 Digitransit Bus Timetables for Home Assistant

Display real-time Finnish bus schedules from Digitransit API in your Home Assistant dashboard.

## Features

- ✅ **Real-time departures** - Shows actual GPS-tracked departure times
- ✅ **Multiple stops** - Monitor up to 2 bus stops (easily expandable)
- ✅ **Auto-refresh** - Updates every 60 seconds
- ✅ **Delay indicators** - Visual indicator (🔴) for real-time tracked buses
- ✅ **Flexible display** - 4 different Lovelace card options
- ✅ **Finnish cities** - Works with any Digitransit-powered city (Helsinki, Tampere, Turku, Oulu, etc.)

## Supported Cities

This integration works with all Finnish cities using Digitransit:
- **Helsinki (HSL)** - Helsinki, Espoo, Vantaa, Kauniainen, Kerava, Kirkkonummi, Sipoo
- **Tampere**
- **Turku**
- **Oulu**
- **Kuopio**
- **Lahti**
- **Vaasa**
- **Jyväskylä**
- **Lappeenranta**
- **Joensuu**
- **Hämeenlinna**
- **Kotka**
- **Mikkeli**
- **Rovaniemi**

## What You Get

After installation, you'll have:
- **5 sensors** per configuration
- **Real-time departure data** with delay information
- **Ready-to-use Lovelace cards** for dashboard
- **Customizable templates** for any display format

## Requirements

- Home Assistant 2023.1.0 or newer
- Digitransit API subscription key (free from [digitransit.fi](https://digitransit.fi))
- REST and Template integrations (built-in)

## Quick Setup

1. Get your free API key from [digitransit.fi](https://digitransit.fi)
2. Find your bus stop codes from your city's Digitransit site
3. Configure REST sensors with your stops
4. Add template sensors
5. Add Lovelace card to dashboard

Full installation guide in [README.md](https://github.com/valtteri-aho/Hassio-digitransit/blob/main/README.md)

## Support

- 📖 [Full Documentation](https://github.com/valtteri-aho/Hassio-digitransit)
- 🐛 [Report Issues](https://github.com/valtteri-aho/Hassio-digitransit/issues)
- 💬 [Home Assistant Community](https://community.home-assistant.io/)
