"""Sensor platform for Open-Meteo Air Quality."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONCENTRATION_MICROGRAMS_PER_CUBIC_METER
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import COORDINATOR, DOMAIN
from .coordinator import AIR_QUALITY_FIELDS

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


@dataclass(frozen=True, kw_only=True)
class OpenMeteoSensorDescription(SensorEntityDescription):
    api_key: str


def _pretty_name(field: str) -> str:
    return field.replace("_", " ").upper()


def _unit_for_field(field: str):
    if field in MICROGRAM_FIELDS:
        return CONCENTRATION_MICROGRAMS_PER_CUBIC_METER
    if field in {"aerosol_optical_depth"}:
        return None
    if field in {"uv_index", "uv_index_clear_sky"}:
        return None
    if "pollen" in field:
        return None
    if field in AQI_FIELDS:
        return None
    return None


SENSOR_DESCRIPTIONS: tuple[OpenMeteoSensorDescription, ...] = tuple(
    OpenMeteoSensorDescription(
        key=field,
        name=_pretty_name(field),
        native_unit_of_measurement=_unit_for_field(field),
        api_key=field,
    )
    for field in AIR_QUALITY_FIELDS
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
        for description in SENSOR_DESCRIPTIONS
    )


class OpenMeteoSensorEntity(CoordinatorEntity, SensorEntity):
    """Representation of an Open-Meteo air quality sensor."""

    _attr_has_entity_name = True

    def __init__(self, coordinator, entry: ConfigEntry, description: OpenMeteoSensorDescription) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_name = description.name

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get(self.entity_description.api_key)

    @property
    def extra_state_attributes(self):
        """Return extra attributes."""
        meta = self.coordinator.data.get("_meta", {})
        return {
            "source": "open-meteo",
            "latitude": meta.get("latitude"),
            "longitude": meta.get("longitude"),
            "timezone": meta.get("timezone"),
            "elevation": meta.get("elevation"),
        }
