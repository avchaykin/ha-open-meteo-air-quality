# Open-Meteo Air Quality (Home Assistant)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=avchaykin&repository=ha-open-meteo-air-quality&category=integration)

A custom Home Assistant integration that fetches air quality metrics from the Open-Meteo Air Quality API.

## Features

- UI-based setup (no `configuration.yaml` required)
- Two location source modes:
  - Home Assistant zone
  - Manual coordinates
- Multi-entry support for multiple locations/zones
- Configurable `scan_interval` via integration Options
- Sensors for key Open-Meteo Air Quality fields:
  - European AQI / US AQI (+ breakdown)
  - PM10 / PM2.5
  - NO2 / SO2 / O3 / CO / ammonia / dust
  - UV index / UV clear sky
  - Pollen (alder, birch, grass, mugwort, olive, ragweed)

## Installation (HACS)

1. Click the button above **or** open HACS → **Integrations** → menu (⋮) → **Custom repositories**.
2. Add repository: `https://github.com/avchaykin/ha-open-meteo-air-quality`.
3. Category: **Integration**.
4. Install **Open-Meteo Air Quality**.
5. Home Assistant → **Settings → Devices & Services → Add Integration**.
6. Select **Open-Meteo Air Quality** and choose location source:
   - Home Assistant zone, or
   - Manual coordinates.

> After adding, all integration settings are managed from the UI.
