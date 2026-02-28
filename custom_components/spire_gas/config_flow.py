from __future__ import annotations

import asyncio
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import SpireClient, SpireApiError, SpireAuthError
from .const import DOMAIN, CONF_USERNAME, CONF_PASSWORD, CONF_ACCOUNT_ID, CONF_SA_ID, HTTP_TIMEOUT_SECONDS


class SpireGasConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            session = async_get_clientsession(self.hass)
            client = SpireClient(session, user_input[CONF_USERNAME], user_input[CONF_PASSWORD])

            try:
                await asyncio.wait_for(client.login_only(), timeout=HTTP_TIMEOUT_SECONDS + 10)
            except SpireAuthError:
                errors["base"] = "invalid_auth"
            except (SpireApiError, asyncio.TimeoutError):
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(f"{user_input[CONF_ACCOUNT_ID]}:{user_input[CONF_SA_ID]}")
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"Spire Gas ({user_input[CONF_SA_ID]})",
                    data={
                        CONF_USERNAME: user_input[CONF_USERNAME],
                        CONF_PASSWORD: user_input[CONF_PASSWORD],
                        CONF_ACCOUNT_ID: str(user_input[CONF_ACCOUNT_ID]),
                        CONF_SA_ID: str(user_input[CONF_SA_ID]),
                    },
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_PASSWORD): str,
                vol.Required(CONF_ACCOUNT_ID): str,
                vol.Required(CONF_SA_ID): str,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
