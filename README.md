# Open-Meteo Air Quality (Home Assistant)

A custom Home Assistant integration that fetches air quality metrics from the Open-Meteo Air Quality API.

## Features

- UI-based setup (no `configuration.yaml` required)
- Two location source modes:
  - Home Assistant zone
  - Manual coordinates
- Multi-entry support for multiple locations/zones
- `DataUpdateCoordinator` with scheduled polling
- Configurable `scan_interval` via Options (no restart required)
- Sensors for key Open-Meteo Air Quality fields:
  - European AQI / US AQI (+ breakdown)
  - PM10 / PM2.5
  - NO2 / SO2 / O3 / CO / ammonia / dust
  - UV index / UV clear sky
  - Pollen (alder, birch, grass, mugwort, olive, ragweed)
- MDI icons for integration and sensors (including `mdi:flower-pollen` for pollen)

## Installation via HACS

1. HACS → **Integrations** → menu (⋮) → **Custom repositories**
2. Add repository: `https://github.com/avchaykin/ha-open-meteo-air-quality`
3. Category: **Integration**
4. Install **Open-Meteo Air Quality**
5. Home Assistant → **Settings → Devices & Services → Add Integration**
6. Select **Open-Meteo Air Quality** and choose location source:
   - Home Assistant zone, or
   - Manual coordinates

> After adding, all integration settings are managed from the UI.

## Configuration

Available in Options:
- `scan_interval` — update interval in minutes (5–180)

## HACS Release Workflow (for maintainers)

### Standard release process

1. Update version in `custom_components/open_meteo_air_quality/manifest.json`.
2. Commit changes to `main`.
3. Create and push tag `vX.Y.Z`.
4. Create a GitHub Release for that tag.
5. In HACS, run **Check for updates**.

### If HACS does not show the update

1. Confirm `manifest.json` version was incremented.
2. Confirm both tag and GitHub Release exist and match the same version.
3. Confirm tag format is exactly `vX.Y.Z`.
4. In HACS, reload/refresh and check updates again.
5. Restart Home Assistant if HACS cache is stale.
6. Verify the release tag points to the expected commit.

## Status

- Current release: `v0.2.1`
- Repository: https://github.com/avchaykin/ha-open-meteo-air-quality

## Roadmap

- Improve user-facing documentation (Lovelace card examples)
- Add automated tests (at least smoke + config flow)
