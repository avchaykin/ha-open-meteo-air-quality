"""DataUpdateCoordinator for Open-Meteo Air Quality."""

from __future__ import annotations

from datetime import datetime, timedelta
import logging
from typing import Any
from zoneinfo import ZoneInfo

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DEFAULT_SCAN_INTERVAL_MIN, DOMAIN

_LOGGER = logging.getLogger(__name__)

BASE_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"

# Поля, которые запрашиваем у Open-Meteo. Для каждого будет создан сенсор.
AIR_QUALITY_FIELDS: tuple[str, ...] = (
    "european_aqi",
    "european_aqi_pm2_5",
    "european_aqi_pm10",
    "european_aqi_nitrogen_dioxide",
    "european_aqi_ozone",
    "european_aqi_sulphur_dioxide",
    "us_aqi",
    "us_aqi_pm2_5",
    "us_aqi_pm10",
    "us_aqi_nitrogen_dioxide",
    "us_aqi_carbon_monoxide",
    "us_aqi_ozone",
    "us_aqi_sulphur_dioxide",
    "pm10",
    "pm2_5",
    "carbon_monoxide",
    "nitrogen_dioxide",
    "sulphur_dioxide",
    "ozone",
    "aerosol_optical_depth",
    "dust",
    "ammonia",
    "uv_index",
    "uv_index_clear_sky",
    "alder_pollen",
    "birch_pollen",
    "grass_pollen",
    "mugwort_pollen",
    "olive_pollen",
    "ragweed_pollen",
)

POLLEN_FIELDS: tuple[str, ...] = tuple(field for field in AIR_QUALITY_FIELDS if "pollen" in field)


class OpenMeteoAirQualityCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinate Open-Meteo Air Quality API fetches."""

    def __init__(self, hass: HomeAssistant, entry) -> None:
        self.hass = hass
        self.entry = entry
        self._session = async_get_clientsession(hass)

        scan_interval = timedelta(
            minutes=entry.options.get("scan_interval", DEFAULT_SCAN_INTERVAL_MIN)
        )

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{entry.entry_id}",
            update_interval=scan_interval,
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from Open-Meteo Air Quality API."""
        latitude = self.entry.data["latitude"]
        longitude = self.entry.data["longitude"]

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": ",".join(AIR_QUALITY_FIELDS),
            "timezone": "auto",
        }

        try:
            async with self._session.get(BASE_URL, params=params, timeout=20) as response:
                if response.status != 200:
                    text = await response.text()
                    raise UpdateFailed(
                        f"Open-Meteo API error {response.status}: {text[:300]}"
                    )

                payload = await response.json()
        except Exception as err:
            raise UpdateFailed(f"Error requesting Open-Meteo API: {err}") from err

        hourly = payload.get("hourly", {})
        values: dict[str, Any] = {}

        index = self._resolve_current_hour_index(payload)

        for field in AIR_QUALITY_FIELDS:
            series = hourly.get(field)
            values[field] = self._series_value(series, index)

        values["_meta"] = {
            "latitude": payload.get("latitude"),
            "longitude": payload.get("longitude"),
            "timezone": payload.get("timezone"),
            "elevation": payload.get("elevation"),
            "selected_time": (hourly.get("time") or [None])[index] if hourly.get("time") else None,
        }
        values["_pollen_forecast"] = self._build_pollen_forecast(payload, index)

        return values

    def _resolve_current_hour_index(self, payload: dict) -> int:
        hourly = payload.get("hourly", {})
        times = hourly.get("time")
        if not isinstance(times, list) or not times:
            return 0

        tz_name = payload.get("timezone") or "UTC"
        try:
            tz = ZoneInfo(tz_name)
        except Exception:
            tz = ZoneInfo("UTC")

        now_key = datetime.now(tz).replace(minute=0, second=0, microsecond=0).strftime(
            "%Y-%m-%dT%H:00"
        )
        if now_key in times:
            return times.index(now_key)

        # Fallback: первая доступная точка.
        return 0

    def _build_pollen_forecast(self, payload: dict[str, Any], current_index: int) -> dict[str, dict[str, Any]]:
        """Build compact forecast aggregates for pollen metrics."""
        hourly = payload.get("hourly", {})
        times = hourly.get("time")
        if not isinstance(times, list) or not times:
            return {}

        tz_name = payload.get("timezone") or "UTC"
        try:
            tz = ZoneInfo(tz_name)
        except Exception:
            tz = ZoneInfo("UTC")

        parsed_times: list[datetime] = []
        for ts in times:
            try:
                parsed_times.append(datetime.fromisoformat(ts).replace(tzinfo=tz))
            except Exception:
                parsed_times.append(None)

        forecast: dict[str, dict[str, Any]] = {}

        for field in POLLEN_FIELDS:
            series = hourly.get(field)
            if not isinstance(series, list) or not series:
                continue

            daily_max: dict[str, float] = {}
            for idx, raw_value in enumerate(series):
                if idx >= len(parsed_times):
                    break
                dt = parsed_times[idx]
                if dt is None or raw_value is None:
                    continue

                try:
                    value = float(raw_value)
                except (TypeError, ValueError):
                    continue

                day_key = dt.date().isoformat()
                if day_key not in daily_max or value > daily_max[day_key]:
                    daily_max[day_key] = value

            next_24h_values: list[float] = []
            upper_bound = min(len(series), current_index + 24)
            for idx in range(current_index, upper_bound):
                raw_value = series[idx]
                if raw_value is None:
                    continue
                try:
                    next_24h_values.append(float(raw_value))
                except (TypeError, ValueError):
                    continue

            forecast[field] = {
                "daily_max": daily_max,
                "next_24h_max": max(next_24h_values) if next_24h_values else None,
            }

        return forecast

    @staticmethod
    def _series_value(series, index: int):
        if not isinstance(series, list) or not series:
            return None
        if index < len(series):
            return series[index]
        return series[0]
