from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult

from .const import DOMAIN


class MobilusConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(
                title=user_input["host"],
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=self._data_schema(),
        )

    async def async_step_reconfigure(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
         reconfigure_entry = self.hass.config_entries.async_get_entry(
             self.context["entry_id"],
         )

         if reconfigure_entry is None:
            return self.async_abort(reason="entry_not_found")

         if user_input is not None:
            return self.async_update_reload_and_abort(
                entry=reconfigure_entry,
                data=user_input,
                reason="reconfigure_successful",
            )

         return self.async_show_form(
             step_id="reconfigure",
             data_schema=self._data_schema(dict(reconfigure_entry.data)),
         )

    def _data_schema(self, defaults: dict[str, Any] | None = None) -> vol.Schema:
        defaults = defaults or {}

        return vol.Schema({
            vol.Required("host", default=defaults.get("host", None)): str,
            vol.Required("username", default=defaults.get("username", None)): str,
            vol.Required("password", default=defaults.get("password", None)): str,
        })
