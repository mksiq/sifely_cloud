import logging
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
import voluptuous as vol

from .const import (
    DOMAIN,
    CONF_EMAIL,
    CONF_PASSWORD,
    CONF_CLIENT_ID,
)

_LOGGER = logging.getLogger(__name__)


class SifelyCloudConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Sifely Cloud."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        errors = {}

        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            # Optionally: test credentials here if needed
            # if not await self._test_credentials(user_input):
            #     errors["base"] = "auth"
            #     return await self._show_form(user_input, errors)

            return self.async_create_entry(
                title=user_input[CONF_EMAIL],
                data={},
                options=user_input,
            )

        # First-time: show blank form
        return await self._show_form(user_input={}, errors={})

    async def _show_form(self, user_input, errors) -> FlowResult:
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_EMAIL, default=user_input.get(CONF_EMAIL, "")): str,
                vol.Required(CONF_PASSWORD, default=user_input.get(CONF_PASSWORD, "")): str,
                vol.Required(CONF_CLIENT_ID, default=user_input.get(CONF_CLIENT_ID, "")): str,
            }),
            errors=errors
        )


class SifelyCloudOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options for Sifely Cloud."""

    def __init__(self, config_entry: config_entries.ConfigEntry):
        self.config_entry = config_entry

    async def async_step_user(self, user_input=None) -> FlowResult:
        _LOGGER.warning("✅ OptionsFlow INIT triggered! Options: %s", self.config_entry.options)

        def default(key, fallback=""):
            return self.config_entry.options.get(key, self.config_entry.data.get(key, fallback))

        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(CONF_EMAIL, default=default(CONF_EMAIL)): str,
                vol.Required(CONF_PASSWORD, default=default(CONF_PASSWORD)): str,
                vol.Required(CONF_CLIENT_ID, default=default(CONF_CLIENT_ID)): str,
            }),
        )


@callback
def async_get_options_flow(config_entry: config_entries.ConfigEntry):
    return SifelyCloudOptionsFlowHandler(config_entry)
