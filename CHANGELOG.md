# Changelog

All notable changes to this project will be documented here.

## [1.2.0] - 2026-02-28

### Added
- Automatic refresh every 6 hours to pick up new Spire readings
- Only appends new data points on each refresh — does not rewrite history

### Changed
- Live API fetch replaces static data

## [1.1.0] - 2026-02-28

### Added
- Live data fetch from Spire Energy API on setup

### Removed
- Static hardcoded data

## [1.0.0] - 2026-02-28

Initial public release.

- Fetches daily gas usage history from Spire Energy API
- Displays in Home Assistant Energy dashboard in CCF
- UI-based configuration via config flow
- HACS compatible
