# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-01-07

### Added
- Initial release of Digitransit Bus Timetables for Home Assistant
- REST sensor configuration for Digitransit API v2
- Template sensors for formatting bus departure data
- 4 different Lovelace card options (vertical stack, markdown, entities, conditional)
- Support for all Finnish cities using Digitransit (HSL, Waltti regions)
- Real-time GPS tracking with visual indicators
- Configurable number of departures per stop (default 5)
- Auto-refresh every 60 seconds (configurable)
- Minutes-to-departure countdown
- HACS compatibility with metadata files
- Complete documentation with troubleshooting guide
- Example configuration files with placeholders
- MIT License

### Features
- Monitor up to 2 bus stops simultaneously (easily expandable)
- Display route number, destination, scheduled time, and countdown
- Real-time delay indicators (🔴 emoji)
- Multi-stop combined view
- Conditional visibility (workday/time-based)
- GraphQL query support for Digitransit API

### Documentation
- Comprehensive README with installation guide
- City-specific router and stop code examples
- Troubleshooting section
- Customization examples
- Automation examples
- Contributing guidelines

[0.1.0]: https://github.com/valtteri-aho/Hassio-digitransit/releases/tag/v0.1.0
