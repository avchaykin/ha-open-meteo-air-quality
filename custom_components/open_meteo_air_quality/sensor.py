"""Sensor platform for Open-Meteo Air Quality."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONCENTRATION_MICROGRAMS_PER_CUBIC_METER
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_ZONE_ENTITY_ID, CONF_ZONE_NAME, COORDINATOR, DOMAIN
from .coordinator import AIR_QUALITY_FIELDS, POLLEN_FIELDS

AQI_FIELDS = {field for field in AIR_QUALITY_FIELDS if "aqi" in field}
MICROGRAM_FIELDS = {
    "pm10",
    "pm2_5",
    "carbon_monoxide",
    "nitrogen_dioxide",
    "sulphur_dioxide",
    "ozone",
    "ammonia",
    "dust",
}
POLLEN_UNIT = "grains/m³"


@dataclass(frozen=True, kw_only=True)
class OpenMeteoSensorDescription(SensorEntityDescription):
    api_key: str
    kind: str = "current"


def _pretty_name(field: str) -> str:
    return field.replace("_", " ").upper()


def _icon_for_field(field: str) -> str | None:
    if "pollen" in field:
        return "mdi:flower-pollen"
    if field in {"pm10", "pm2_5", "dust"}:
        return "mdi:blur"
    if field == "carbon_monoxide":
        return "mdi:molecule-co"
    if field == "nitrogen_dioxide":
        return "mdi:molecule"
    if field == "sulphur_dioxide":
        return "mdi:molecule"
    if field == "ozone":
        return "mdi:weather-windy"
    if field == "ammonia":
        return "mdi:molecule"
    if "aqi" in field:
        return "mdi:gauge"
    if field in {"uv_index", "uv_index_clear_sky"}:
        return "mdi:weather-sunny-alert"
    if field == "aerosol_optical_depth":
        return "mdi:weather-hazy"
    return "mdi:chart-line"


def _unit_for_field(field: str):
    if field in MICROGRAM_FIELDS:
        return CONCENTRATION_MICROGRAMS_PER_CUBIC_METER
    if "pollen" in field:
        return POLLEN_UNIT
    if field in {"aerosol_optical_depth"}:
        return None
    if field in {"uv_index", "uv_index_clear_sky"}:
        return None
    if field in AQI_FIELDS:
        return None
    return None


def _state_class_for_field(field: str) -> SensorStateClass | None:
    if field in {"aerosol_optical_depth", "uv_index", "uv_index_clear_sky"}:
        return SensorStateClass.MEASUREMENT
    if field in MICROGRAM_FIELDS:
        return SensorStateClass.MEASUREMENT
    if "pollen" in field:
        return SensorStateClass.MEASUREMENT
    if field in AQI_FIELDS:
        return SensorStateClass.MEASUREMENT
    return None


def _banded_label(value: float, bands: list[tuple[float, str]]) -> str:
    for threshold, label in bands:
        if value <= threshold:
            return label
    return bands[-1][1]


def _scale_label(field: str, value: Any) -> str | None:
    if value is None:
        return None

    try:
        num = float(value)
    except (TypeError, ValueError):
        return None

    if "pollen" in field:
        return _banded_label(
            num,
            [
                (0, "none"),
                (10, "very_low"),
                (30, "low"),
                (80, "moderate"),
                (200, "high"),
                (500, "very_high"),
                (999999, "extremely_high"),
            ],
        )

    if field in AQI_FIELDS:
        return _banded_label(
            num,
            [
                (50, "good"),
                (100, "moderate"),
                (150, "unhealthy_for_sensitive"),
                (200, "unhealthy"),
                (300, "very_unhealthy"),
                (999999, "hazardous"),
            ],
        )

    if field in {"uv_index", "uv_index_clear_sky"}:
        return _banded_label(
            num,
            [
                (2.99, "low"),
                (5.99, "moderate"),
                (7.99, "high"),
                (10.99, "very_high"),
                (999999, "extreme"),
            ],
        )

    if field in {"pm2_5", "pm10"}:
        # Reference: WHO-like interpretation bands for quick dashboard guidance.
        return _banded_label(
            num,
            [
                (15, "good"),
                (45, "moderate"),
                (75, "unhealthy_for_sensitive"),
                (150, "unhealthy"),
                (999999, "very_unhealthy"),
            ],
        )

    if field == "aerosol_optical_depth":
        return _banded_label(
            num,
            [
                (0.1, "clear"),
                (0.3, "light_haze"),
                (0.6, "hazy"),
                (999999, "very_hazy"),
            ],
        )

    return None


CURRENT_SENSOR_DESCRIPTIONS: tuple[OpenMeteoSensorDescription, ...] = tuple(
    OpenMeteoSensorDescription(
        key=field,
        name=_pretty_name(field),
        native_unit_of_measurement=_unit_for_field(field),
        state_class=_state_class_for_field(field),
        icon=_icon_for_field(field),
        api_key=field,
        kind="current",
    )
    for field in AIR_QUALITY_FIELDS
)

POLLEN_NEXT_24H_SENSOR_DESCRIPTIONS: tuple[OpenMeteoSensorDescription, ...] = tuple(
    OpenMeteoSensorDescription(
        key=f"{field}_next_24h_max",
        name=f"{_pretty_name(field)} NEXT 24H MAX",
        native_unit_of_measurement=POLLEN_UNIT,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:flower-pollen",
        api_key=field,
        kind="next_24h_max",
    )
    for field in POLLEN_FIELDS
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]

    async_add_entities(
        OpenMeteoSensorEntity(coordinator, entry, description)
        for description in (*CURRENT_SENSOR_DESCRIPTIONS, *POLLEN_NEXT_24H_SENSOR_DESCRIPTIONS)
    )


class OpenMeteoSensorEntity(CoordinatorEntity, SensorEntity):
    """Representation of an Open-Meteo air quality sensor."""

    _attr_has_entity_name = True

    def __init__(self, coordinator, entry: ConfigEntry, description: OpenMeteoSensorDescription) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_name = description.name

        zone_name = entry.data.get(CONF_ZONE_NAME)
        self._attr_suggested_area = zone_name if zone_name else None

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        zone_name = self._entry.data.get(CONF_ZONE_NAME, "Manual coordinates")
        identifiers = {(DOMAIN, self._entry.entry_id)}

        return DeviceInfo(
            identifiers=identifiers,
            name=f"Open-Meteo Air Quality ({zone_name})",
            manufacturer="Open-Meteo",
            model="Air Quality API",
            configuration_url=(
                f"https://www.openstreetmap.org/?mlat={self._entry.data.get('latitude')}&mlon={self._entry.data.get('longitude')}"
            ),
        )

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if self.entity_description.kind == "next_24h_max":
            pollen_forecast = self.coordinator.data.get("_pollen_forecast", {})
            return pollen_forecast.get(self.entity_description.api_key, {}).get("next_24h_max")

        return self.coordinator.data.get(self.entity_description.api_key)

    @property
    def extra_state_attributes(self):
        """Return extra attributes."""
        meta = self.coordinator.data.get("_meta", {})
        value = self.native_value
        attributes = {
            "source": "open-meteo",
            "latitude": meta.get("latitude"),
            "longitude": meta.get("longitude"),
            "timezone": meta.get("timezone"),
            "elevation": meta.get("elevation"),
            "zone_entity_id": self._entry.data.get(CONF_ZONE_ENTITY_ID),
            "zone_name": self._entry.data.get(CONF_ZONE_NAME),
            "scale_level": _scale_label(self.entity_description.api_key, value),
        }

        pollen_forecast = self.coordinator.data.get("_pollen_forecast", {})
        field_forecast = pollen_forecast.get(self.entity_description.api_key, {})

        if self.entity_description.kind == "next_24h_max":
            attributes["forecast_window"] = "next_24h"
            return attributes

        if self.entity_description.api_key in POLLEN_FIELDS:
            daily_max = field_forecast.get("daily_max", {})
            day_keys = sorted(daily_max.keys())
            if day_keys:
                attributes["forecast_today_max"] = daily_max.get(day_keys[0])
            if len(day_keys) > 1:
                attributes["forecast_tomorrow_max"] = daily_max.get(day_keys[1])
            for offset, day_key in enumerate(day_keys[2:], start=2):
                attributes[f"forecast_day_{offset}_max"] = daily_max.get(day_key)

        return attributes
