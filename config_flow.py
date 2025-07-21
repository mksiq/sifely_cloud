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
    CONF_APX_NUM_LOCKS,
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
            # Validate and create entry
            return self.async_create_entry(
                title=user_input[CONF_EMAIL],
                data={},
                options=user_input,
            )

        return await self._show_form(user_input={}, errors=errors)

    async def _show_form(self, user_input, errors) -> FlowResult:
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_EMAIL, default=user_input.get(CONF_EMAIL, "")): str,
                vol.Required(CONF_PASSWORD, default=user_input.get(CONF_PASSWORD, "")): str,
                vol.Required(CONF_CLIENT_ID, default=user_input.get(CONF_CLIENT_ID, "")): str,
                vol.Required(CONF_APX_NUM_LOCKS, default=user_input.get(CONF_APX_NUM_LOCKS, 5)): vol.In([5, 10, 15, 20, 25, 30, 35, 40, 45, 50]),
            }),
            errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Expose the options flow handler for the gear icon."""
        return SifelyCloudOptionsFlowHandler(config_entry)


class SifelyCloudOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options for Sifely Cloud."""

    def __init__(self, config_entry: config_entries.ConfigEntry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None) -> FlowResult:
        """Initial step for options flow (gear icon)."""
        return await self.async_step_user(user_input)

    async def async_step_user(self, user_input=None) -> FlowResult:
        _LOGGER.debug("⚙️ OptionsFlow triggered with current options: %s", self.config_entry.options)

        def default(key, fallback=""):
            return self.config_entry.options.get(key, self.config_entry.data.get(key, fallback))

        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_EMAIL, default=default(CONF_EMAIL)): str,
                vol.Required(CONF_PASSWORD, default=default(CONF_PASSWORD)): str,
                vol.Required(CONF_CLIENT_ID, default=default(CONF_CLIENT_ID)): str,
                vol.Required(CONF_APX_NUM_LOCKS, default=default(CONF_APX_NUM_LOCKS, 5)): vol.In([5, 10, 15, 20, 25, 30, 35, 40, 45, 50]),
            }),
        )

