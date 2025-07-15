"""Sifely Cloud Custom - Constants."""

# Base component constants
DOMAIN = "sifely_cloud_custom"
VERSION = "2025.07.15"

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
