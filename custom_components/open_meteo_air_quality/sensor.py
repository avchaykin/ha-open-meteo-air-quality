"""Sensor platform for Open-Meteo Air Quality."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfConcentrationMicrogramsPerCubicMeter
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback


@dataclass(frozen=True, kw_only=True)
class OpenMeteoSensorDescription(SensorEntityDescription):
    api_key: str


SENSOR_DESCRIPTIONS: tuple[OpenMeteoSensorDescription, ...] = (
    OpenMeteoSensorDescription(
        key="pm10",
        name="PM10",
        native_unit_of_measurement=UnitOfConcentrationMicrogramsPerCubicMeter,
        api_key="pm10",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors from a config entry."""
    async_add_entities(OpenMeteoSensorEntity(entry, description) for description in SENSOR_DESCRIPTIONS)


class OpenMeteoSensorEntity(SensorEntity):
    """Representation of an Open-Meteo air quality sensor."""

    _attr_has_entity_name = True

    def __init__(self, entry: ConfigEntry, description: OpenMeteoSensorDescription) -> None:
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_name = description.name
        self._attr_native_value = None
