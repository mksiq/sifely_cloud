import logging
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


def async_register_lock_device(lock_data: dict) -> DeviceInfo:
    """Create and return DeviceInfo for a Sifely lock entity."""

    lock_id = lock_data.get("lockId")
    alias = lock_data.get("lockAlias", "Sifely Lock")
    mac = lock_data.get("lockMac", f"sifely_{lock_id or 'unknown'}")
    model = lock_data.get("lockName", "Sifely")
    sw_version = None

    if not lock_id:
        _LOGGER.warning("⚠️ Lock data missing 'lockId': %s", lock_data)

    # Build software version string from lockVersion.scene if available
    version_info = lock_data.get("lockVersion")
    if isinstance(version_info, dict):
        scene = version_info.get("scene")
        if scene is not None:
            sw_version = f"Scene {scene}"

    return DeviceInfo(
        identifiers={(DOMAIN, str(lock_id))},
        name=alias,
        manufacturer="Sifely",
        model=model,
        sw_version=sw_version,
        via_device=None,  # Replace if nested under a gateway device later
    )
