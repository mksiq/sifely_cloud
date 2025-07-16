# __init__.py
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .token_manager import SifelyTokenManager
from .const import (
    DOMAIN,
    CONF_EMAIL,
    CONF_PASSWORD,
    CONF_CLIENT_ID,
    CONF_TOKEN_REFRESH,
    STARTUP_MESSAGE,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict):
    """Handle YAML setup (unused)."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Handle integration setup from config flow."""
    _LOGGER.info("📦 Setting up Sifely Cloud with options: %s", entry.options)

    if hass.data.get(DOMAIN) is None:
        hass.data[DOMAIN] = {}
        _LOGGER.info(STARTUP_MESSAGE)

    # Extract credentials from options
    email = entry.options.get(CONF_EMAIL)
    password = entry.options.get(CONF_PASSWORD)
    client_id = entry.options.get(CONF_CLIENT_ID)
    token_refresh = entry.options.get(CONF_TOKEN_REFRESH, 60)

    if not all([email, password, client_id]):
        _LOGGER.error("❌ Missing required credentials in config entry.")
        return False

    _LOGGER.info("🔐 Requesting Sifely token with client_id: %s", client_id)

    # Create token manager and log in
    session = async_get_clientsession(hass)
    token_manager = SifelyTokenManager(client_id, email, password, session)

    try:
        await token_manager.refresh_token_func()
        _LOGGER.info("✅ Sifely token initialized successfully.")
    except Exception as e:
        _LOGGER.exception("❌ Failed to authenticate with Sifely")
        return False

    # Store the token manager for use in other platforms (e.g., lock)
    hass.data[DOMAIN][entry.entry_id] = token_manager
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Handle removal of an entry."""
    hass.data[DOMAIN].pop(entry.entry_id, None)
    return True

