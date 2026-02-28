"""Config flow for Gas Test integration."""
import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN


class GasTestConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Gas Test."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            # Only allow one instance
            await self.async_set_unique_id(DOMAIN)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title="Gas Test", data={})

        return self.async_show_form(step_id="user", data_schema=vol.Schema({}))
