"""Sifely Cloud - Constants."""

import os

# Base component constants
NAME = "Sifely Cloud"
DOMAIN = "sifely_cloud"
VERSION = "2025.07.15"
ISSUE_URL = "https://github.com/kenster1965/sifely_cloud/issues"

CONF_EMAIL = "User_Email"
CONF_PASSWORD = "User_Password"
CONF_CLIENT_ID = "clientId"
CONF_CLIENT_SECRET = "clientSecret"
CONF_TOKEN_REFRESH = "token_refresh"

CONFIG_FILE = "secrets.yaml"
CONFIG_PATH = os.path.join("/config", CONFIG_FILE)

TOKEN_FILE = "sifely_token.json"
TOKEN_PATH = os.path.join("/config", TOKEN_FILE)

API_BASE_URL = "https://app-smart-server.sifely.com/system/smart"
TOKEN_ENDPOINT = f"{API_BASE_URL}/login"
REFRESH_ENDPOINT = "https://app-smart-server.sifely.com/system/smart/refreshToken"

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

STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom integration!
If there are problems with it, please feel free to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""