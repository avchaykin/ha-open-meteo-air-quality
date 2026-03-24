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
- Sensors for AQI, pollutants, UV, and pollen
- Pollen forecast helpers:
  - Daily max attributes on pollen sensors (`forecast_today_max`, `forecast_tomorrow_max`, `forecast_day_2_max`)
  - Dedicated "next 24h max" pollen sensors for automations

## Installation (HACS)

1. Click the button above **or** open HACS → **Integrations** → menu (⋮) → **Custom repositories**.
2. Add repository: `https://github.com/avchaykin/ha-open-meteo-air-quality`.
3. Category: **Integration**.
4. Install **Open-Meteo Air Quality**.
5. Home Assistant → **Settings → Devices & Services → Add Integration**.
6. Select **Open-Meteo Air Quality** and choose location source:
   - Home Assistant zone, or
   - Manual coordinates.

## Air Quality Metrics Reference

| Metric group | Sensors | Typical unit | Quick interpretation |
|---|---|---:|---|
| AQI (EU/US) | `european_aqi`, `us_aqi` (+ breakdown) | index | 0–50 good, 51–100 moderate, 101–150 unhealthy for sensitive groups, 151+ unhealthy |
| PM2.5 | `pm2_5` | μg/m³ | 0–15 good, 16–45 moderate, 46–75 elevated, 76+ high |
| PM10 | `pm10` | μg/m³ | 0–15 good, 16–45 moderate, 46–75 elevated, 76+ high |
| Gases | `nitrogen_dioxide`, `sulphur_dioxide`, `ozone`, `carbon_monoxide`, `ammonia` | μg/m³ | lower is generally better; compare trends and local standards |
| Dust | `dust` | μg/m³ | lower is generally better |
| UV | `uv_index`, `uv_index_clear_sky` | index | 0–2 low, 3–5 moderate, 6–7 high, 8–10 very high, 11+ extreme |
| Pollen | `alder/birch/grass/mugwort/olive/ragweed_pollen` | grains/m³ | very low, low, moderate, high, very high, extremely high |
| Aerosol optical depth | `aerosol_optical_depth` | index | lower means clearer atmosphere |

> Notes:
> - The integration also exposes `scale_level` attribute for easier dashboard interpretation.
> - Reference ranges are intended for quick orientation in Home Assistant dashboards.
