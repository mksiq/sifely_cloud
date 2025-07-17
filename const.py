"""Sifely Cloud - Constants."""

import os

# Base component constants
NAME = "Sifely Cloud"
DOMAIN = "sifely_cloud"
VERSION = "2025.07.16"
ISSUE_URL = "https://github.com/kenster1965/sifely_cloud/issues"

CONF_EMAIL = "User_Email"
CONF_PASSWORD = "User_Password"
CONF_CLIENT_ID = "clientId"


# How often to refresh the token if not provided by API
#TOKEN_LIFETIME_MINUTES = 60
TOKEN_LIFETIME_MINUTES = 6
# Buffer time to refresh token early (before actual expiration)
TOKEN_REFRESH_BUFFER_MINUTES = 5

API_BASE_URL = "https://app-smart-server.sifely.com/system/smart"
TOKEN_ENDPOINT = f"{API_BASE_URL}/login"
REFRESH_ENDPOINT = f"{API_BASE_URL}/oauthToken"

# Valid HA entity categories
VALID_ENTITY_CATEGORIES = {
    "config",  "diagnostic",
}

# Valid HA device classes for sensor and number
VALID_SENSOR_CLASSES = {
    "illuminance", "signal_strength", "battery", "timestamp",
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