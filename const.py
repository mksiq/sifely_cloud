"""Sifely Cloud Custom - Constants."""

import os

# Base component constants
DOMAIN = "sifely_cloud_custom"
VERSION = "2025.07.15"

CONF_EMAIL = "User_Email"
CONF_PASSWORD = "User_Password"
CONF_CLIENT_ID = "clientId"
CONF_CLIENT_SECRET = "clientSecret"
CONF_TOKEN_REFRESH = "token_refresh"

TOKEN_FILE = "sifely_token.json"
TOKEN_PATH = os.path.join("/config", TOKEN_FILE)

API_BASE_URL = "https://openapi.sifely.com/v1"
TOKEN_ENDPOINT = f"{API_BASE_URL}/token"

# Valid HA entity categories
VALID_ENTITY_CATEGORIES = {
    "config",
    "diagnostic",
}

# Valid HA device classes for sensor and number
VALID_SENSOR_CLASSES = {
    "illuminance", "signal_strength", "battery",
    "timestamp",
}

# Supported platforms
SUPPORTED_PLATFORMS = {"switch", "sensor", "number"}
