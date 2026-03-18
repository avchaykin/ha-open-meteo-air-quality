"""DataUpdateCoordinator for Open-Meteo Air Quality."""

from __future__ import annotations

from datetime import timedelta
import logging

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


class OpenMeteoAirQualityCoordinator(DataUpdateCoordinator[dict[str, float | int | None]]):
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

    async def _async_update_data(self) -> dict[str, float | int | None]:
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
        values: dict[str, float | int | None] = {}

        for field in AIR_QUALITY_FIELDS:
            series = hourly.get(field)
            values[field] = series[0] if isinstance(series, list) and series else None

        values["_meta"] = {
            "latitude": payload.get("latitude"),
            "longitude": payload.get("longitude"),
            "timezone": payload.get("timezone"),
            "elevation": payload.get("elevation"),
        }

        return values
