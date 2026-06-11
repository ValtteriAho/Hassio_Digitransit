# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.11] - 2026-06-11

### Changed
- Updated `lovelace_card.yaml` examples to use v0.1.10+ attributes (`departures`, `status`, `status_color`, `status_icon`) and include a cleaner Next 3 view.

## [0.1.10] - 2026-06-11

### Added
- Added `status_color` field for each departure (`green`, `red`, `dodgerblue`, `gray`) for Lovelace icon/text coloring.
- Formatted departure lines now include color metadata to help template-card rendering.

## [0.1.9] - 2026-06-11

### Added
- Added status-specific icons for departures and sensors.
- Sensor icon now reflects next departure status:
	- `mdi:clock-check-outline` for on time
	- `mdi:clock-alert-outline` for late
	- `mdi:clock-fast` for early
	- `mdi:clock-outline` for scheduled
- Added `status_icon` field to each departure attribute object.

## [0.1.8] - 2026-06-11

### Added
- Added explicit departure status field (`status`) for each departure item and next-departure data.
- Status now shows one of: `On time`, `Late by X min`, `Early by X min`, or `Scheduled`.

### Changed
- Formatted departure lines (`lahto_1`, `departure_1`, etc.) now include status text for easier visibility in Lovelace cards.

## [0.1.7] - 2026-06-11

### Added
- Added a second sensor per stop for a compact view of the next 3 upcoming departures in state format (`HH:MM | HH:MM | HH:MM`).

### Fixed
- Improved departure filtering so upcoming departure selection consistently uses future departures.

## [0.1.6] - 2026-06-11

### Fixed
- Fixed AttributeError in DigitransitOptionsFlow initialization. Parent class OptionsFlowWithReload already manages config_entry; removed redundant assignment.

## [0.1.5] - 2026-06-11

### Fixed
- **Critical**: Fixed GraphQL query formatting that was causing 400 Bad Request errors. Multi-line query strings were creating invalid JSON. Reformatted to single-line query matching the working config flow format.

## [0.1.4] - 2026-06-11

### Changed
- Clarified in docs that Waltti stop IDs require city/feed prefix with correct capitalization (e.g., `Vaasa:159712` not `vaasa:159712`).
- Fixed config flow form field label for "add another stop" checkbox to display properly instead of raw key name.

## [0.1.3] - 2026-06-10

### Fixed
- Repaired a broken config flow handler definition that caused Home Assistant to show "Invalid handler specified" when adding the integration.
- Removed a remaining unsupported stop example from the config flow stop form.

## [0.1.2] - 2026-06-10

### Fixed
- Stop validation now checks the selected router instead of probing unrelated routers.
- Config flow guidance now uses supported stop ID examples and clearer router-specific messaging.

### Changed
- Updated integration UI text and docs to match the Digitransit API portal and router-specific stop setup.

## [0.1.1] - 2026-06-10

### Changed
- Clarified setup docs to use Digitransit API Management subscription keys.
- Updated API key instructions to point to https://portal-api.digitransit.fi/ in README, INSTALL, and project info docs.

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
[0.1.1]: https://github.com/ValtteriAho/Hassio_Digitransit/releases/tag/v0.1.1
[0.1.2]: https://github.com/ValtteriAho/Hassio_Digitransit/releases/tag/v0.1.2
[0.1.3]: https://github.com/ValtteriAho/Hassio_Digitransit/releases/tag/v0.1.3
[0.1.4]: https://github.com/ValtteriAho/Hassio_Digitransit/releases/tag/v0.1.4
[0.1.5]: https://github.com/ValtteriAho/Hassio_Digitransit/releases/tag/v0.1.5
[0.1.6]: https://github.com/ValtteriAho/Hassio_Digitransit/releases/tag/v0.1.6
[0.1.7]: https://github.com/ValtteriAho/Hassio_Digitransit/releases/tag/v0.1.7
[0.1.8]: https://github.com/ValtteriAho/Hassio_Digitransit/releases/tag/v0.1.8
[0.1.9]: https://github.com/ValtteriAho/Hassio_Digitransit/releases/tag/v0.1.9
[0.1.10]: https://github.com/ValtteriAho/Hassio_Digitransit/releases/tag/v0.1.10
[0.1.11]: https://github.com/ValtteriAho/Hassio_Digitransit/releases/tag/v0.1.11
