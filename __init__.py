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

    if not all([email, password, client_id]):
        _LOGGER.error("❌ Missing required credentials in config entry.")
        return False

    _LOGGER.info("🔐 Initializing Sifely token manager for client_id: %s", client_id)

    # Create token manager and initialize
    session = async_get_clientsession(hass)
    token_manager = SifelyTokenManager(
        client_id=client_id,
        email=email,
        password=password,
        session=session,
        hass=hass,
        config_entry=entry,
    )

    try:
        await token_manager.initialize()
        _LOGGER.info("✅ Sifely token manager initialized successfully.")
    except Exception as e:
        _LOGGER.exception("❌ Failed to initialize Sifely integration")
        return False

    # Store the token manager for use in other platforms
    hass.data[DOMAIN][entry.entry_id] = token_manager
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Handle removal of an entry."""
    token_manager = hass.data[DOMAIN].get(entry.entry_id)
    if token_manager:
        await token_manager.async_shutdown()

    hass.data[DOMAIN].pop(entry.entry_id, None)
    return True
