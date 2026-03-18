"""Config flow for Open-Meteo Air Quality."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import callback

from .const import DEFAULT_SCAN_INTERVAL_MIN, DOMAIN

CONF_SOURCE = "source"
CONF_ZONE_ENTITY_ID = "zone_entity_id"
CONF_ZONE_NAME = "zone_name"
CONF_DEVICE_NAME = "device_name"
SOURCE_MANUAL = "manual"
SOURCE_ZONE = "zone"


class OpenMeteoAirQualityConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Open-Meteo Air Quality."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Select setup source."""
        if user_input is not None:
            if user_input[CONF_SOURCE] == SOURCE_ZONE:
                return await self.async_step_zone()
            return await self.async_step_manual()

        schema = vol.Schema(
            {
                vol.Required(CONF_SOURCE, default=SOURCE_ZONE): vol.In(
                    {SOURCE_ZONE: "Home Assistant zone", SOURCE_MANUAL: "Manual coordinates"}
                )
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema)

    async def async_step_zone(self, user_input=None):
        """Create entry from selected HA zone."""
        zone_entities = self.hass.states.async_entity_ids("zone")

        if not zone_entities:
            return self.async_abort(reason="no_zones")

        if user_input is not None:
            zone_entity_id = user_input[CONF_ZONE_ENTITY_ID]
            zone_state = self.hass.states.get(zone_entity_id)
            if zone_state is None:
                return self.async_abort(reason="zone_not_found")

            latitude = zone_state.attributes.get(CONF_LATITUDE)
            longitude = zone_state.attributes.get(CONF_LONGITUDE)
            if latitude is None or longitude is None:
                return self.async_abort(reason="zone_without_coordinates")

            zone_name = zone_state.name or zone_entity_id
            await self.async_set_unique_id(f"zone:{zone_entity_id}")
            self._abort_if_unique_id_configured()

            title = user_input.get(CONF_DEVICE_NAME) or f"Open-Meteo Air Quality ({zone_name})"
            data = {
                CONF_LATITUDE: float(latitude),
                CONF_LONGITUDE: float(longitude),
                CONF_ZONE_ENTITY_ID: zone_entity_id,
                CONF_ZONE_NAME: zone_name,
            }
            return self.async_create_entry(title=title, data=data)

        schema = vol.Schema(
            {
                vol.Required(CONF_ZONE_ENTITY_ID): vol.In(zone_entities),
                vol.Optional(CONF_DEVICE_NAME): str,
            }
        )
        return self.async_show_form(step_id="zone", data_schema=schema)

    async def async_step_manual(self, user_input=None):
        """Create entry from manual coordinates."""
        if user_input is not None:
            latitude = float(user_input[CONF_LATITUDE])
            longitude = float(user_input[CONF_LONGITUDE])
            await self.async_set_unique_id(f"manual:{latitude:.4f},{longitude:.4f}")
            self._abort_if_unique_id_configured()

            title = user_input.get(CONF_DEVICE_NAME) or "Open-Meteo Air Quality"
            data = {
                CONF_LATITUDE: latitude,
                CONF_LONGITUDE: longitude,
            }
            return self.async_create_entry(title=title, data=data)

        schema = vol.Schema(
            {
                vol.Required(CONF_LATITUDE): vol.Coerce(float),
                vol.Required(CONF_LONGITUDE): vol.Coerce(float),
                vol.Optional(CONF_DEVICE_NAME): str,
            }
        )
        return self.async_show_form(step_id="manual", data_schema=schema)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return OpenMeteoAirQualityOptionsFlowHandler(config_entry)


class OpenMeteoAirQualityOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        schema = vol.Schema(
            {
                vol.Required(
                    "scan_interval",
                    default=self.config_entry.options.get(
                        "scan_interval", DEFAULT_SCAN_INTERVAL_MIN
                    ),
                ): vol.All(vol.Coerce(int), vol.Range(min=5, max=180)),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
