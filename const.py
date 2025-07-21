"""Sifely Cloud - Constants."""

import os

# Base component constants
NAME = "Sifely Cloud"
DOMAIN = "sifely_cloud"
ENTITY_PREFIX = "sifely" # Prefix for entity names
VERSION = "2025.07.16"
ISSUE_URL = "https://github.com/kenster1965/sifely_cloud/issues"

CONF_EMAIL = "User_Email"
CONF_PASSWORD = "User_Password"
CONF_CLIENT_ID = "clientId"
CONF_APX_NUM_LOCKS = "apxNumLocks" # Approximate number of locks


# Polling Intervals (in seconds)
DETAILS_UPDATE_INTERVAL = 3600  # e.g., 1 hour for Lock details
STATE_QUERY_INTERVAL = 60       # e.g., 60 seconds for Lock state


HISTORY_DISPLAY_LIMIT = 10  # Limit for history display in UI
LOCK_REQUEST_RETRIES = 3  # Number of retries for lock/unlock requests
TOKEN_REFRESH_BUFFER_MINUTES = 5 # Buffer time to refresh token early (before actual expiration)
TOKEN_401s_BEFORE_REAUTH = 5  # Number of 401 errors before re-authentication
TOKEN_401s_BEFOR_ALERT = 10  # Number of 401 errors before alerting user


# API endpoints
API_BASE_URL = "https://app-smart-server.sifely.com"
TOKEN_ENDPOINT = f"{API_BASE_URL}/system/smart/login"
REFRESH_ENDPOINT = f"{API_BASE_URL}/system/smart/oauthToken"
KEYLIST_ENDPOINT = f"{API_BASE_URL}/v3/key/list"
LOCK_DETAIL_ENDPOINT = f"{API_BASE_URL}/v3/lock/detail"
QUERY_STATE_ENDPOINT = f"{API_BASE_URL}/v3/lock/queryOpenState"
UNLOCK_ENDPOINT = f"{API_BASE_URL}/v3/lock/unlock"
LOCK_ENDPOINT = f"{API_BASE_URL}/v3/lock/lock"
LOCK_HISTORY_ENDPOINT = f"{API_BASE_URL}/v3/lockRecord/list"


# Valid HA entity categories
VALID_ENTITY_CATEGORIES = {
    "config",  "diagnostic",
}

# Valid HA device classes for sensor and number
VALID_SENSOR_CLASSES = {
    "illuminance", "signal_strength", "battery", "timestamp",
}

# Supported platforms
SUPPORTED_PLATFORMS = {"lock", "sensor", "button"}

STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom integration!
If there are problems with it, please feel free to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""