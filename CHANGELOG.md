# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-06-10

### Added
- First public release of the `digitransit` Home Assistant custom integration.
- Config-flow setup from Home Assistant UI.
- Multi-stop support within a single integration entry.
- Configurable number of departures per stop.
- Router support for `waltti`, `hsl`, `tampere`, `turku`, `jyvaskyla`, `oulu`, and `lahti`.
- Coordinator-based polling with 60 second update interval.
- Sensor attributes for departures, next departure, route, destination, realtime flag, and delay.
- HACS metadata and installation support.

### Changed
- Documentation updated to config-flow-first setup.
- Legacy YAML files kept as examples and marked as non-primary setup path.
- VS Code workspace setup added for local lint/test workflow.

### Security
- Replaced committed API key values with `YOUR_API_KEY` placeholders.
- Added CI secret scanning.

### Developer Experience
- Added CI workflow for secret scan, lint, and test.
- Added baseline tests for formatting, guardrails, and release metadata consistency.
- Added release checklist to contribution documentation.

[0.1.0]: https://github.com/ValtteriAho/Hassio_Digitransit/releases/tag/v0.1.0
