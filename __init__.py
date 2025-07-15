# __init__.py
import asyncio
import logging
import os
import yaml

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN
from .sifely_api import get_token

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Sifely Cloud Custom integration."""

    async def handle_test_token(call: ServiceCall):
        """Service to test token retrieval."""
        secrets = hass.data.get(DOMAIN, {}).get("secrets")

        if not secrets:
            _LOGGER.error("Secrets not loaded.")
            return

        email = secrets.get("User_Email")
        password = secrets.get("User_Password")
        client_id = secrets.get("clientId")
        client_secret = secrets.get("clientSecret")

        if not all([email, password, client_id, client_secret]):
            _LOGGER.error("Missing one or more secret keys.")
            return

        _LOGGER.info("Testing token retrieval with provided credentials...")
        await get_token(email, password, client_id, client_secret)

    # Load local secrets file: custom_components/sifely_cloud/config/secrets.yaml
    try:
        component_dir = os.path.dirname(__file__)
        secrets_path = os.path.join(component_dir, "config", "secrets.yaml")
        with open(secrets_path, "r") as f:
            secrets = yaml.safe_load(f)
            _LOGGER.debug("Custom secrets.yaml loaded successfully.")
    except Exception as e:
        _LOGGER.exception("Failed to load custom secrets.yaml")
        secrets = {}

    # Save to global domain store
    hass.data.setdefault(DOMAIN, {})["secrets"] = secrets

    # Register the test service
    hass.services.async_register(DOMAIN, "test_token", handle_test_token)

    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    return True
