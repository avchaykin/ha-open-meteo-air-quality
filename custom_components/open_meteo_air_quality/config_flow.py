"""Config flow for Open-Meteo Air Quality."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .const import DEFAULT_SCAN_INTERVAL_MIN, DOMAIN


class OpenMeteoAirQualityConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Open-Meteo Air Quality."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            await self.async_set_unique_id(
                f"{user_input['latitude']:.4f},{user_input['longitude']:.4f}"
            )
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title="Open-Meteo Air Quality", data=user_input)

        schema = vol.Schema(
            {
                vol.Required("latitude"): vol.Coerce(float),
                vol.Required("longitude"): vol.Coerce(float),
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema)

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
