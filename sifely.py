import logging
import asyncio

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import async_get as async_get_device_registry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .token_manager import SifelyTokenManager
from .const import DOMAIN, KEYLIST_ENDPOINT, CONF_APX_NUM_LOCKS

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up Sifely locks as devices and entities."""
    token_manager: SifelyTokenManager = hass.data[DOMAIN][config_entry.entry_id]
    login_token = token_manager.get_login_token()

    if not login_token:
        _LOGGER.error("❌ Cannot fetch login token from token manager.")
        return

    session = token_manager.session
    apx_locks = config_entry.options.get(CONF_APX_NUM_LOCKS, 5)

    payload = {
        "pageNo": 1,
        "pageSize": apx_locks,
    }

    headers = {
        "Authorization": f"Bearer {login_token}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    try:
        async with session.post(KEYLIST_ENDPOINT, data=payload, headers=headers) as resp:
            data = await resp.json()
            _LOGGER.debug("🔑 Key List response: %s", data)

            if data.get("code") != 200:
                _LOGGER.error("❌ Failed to retrieve lock list: %s", data)
                return

            locks = data.get("data", {}).get("list", [])
            _LOGGER.info("🔓 Discovered %d locks", len(locks))

            for lock in locks:
                await _create_lock_device(hass, config_entry, lock)

    except Exception as e:
        _LOGGER.exception("🚨 Exception while fetching lock list: %s", str(e))


async def _create_lock_device(hass: HomeAssistant, config_entry: ConfigEntry, lock_data: dict):
    """Register a Sifely lock device in Home Assistant."""
    registry = await async_get_device_registry(hass)

    lock_id = str(lock_data.get("lockId"))
    mac = lock_data.get("lockMac")
    alias = lock_data.get("lockAlias", f"Sifely Lock {lock_id}")

    _LOGGER.debug("🆕 Registering lock: %s (%s)", alias, lock_id)

    registry.async_get_or_create(
        config_entry_id=config_entry.entry_id,
        identifiers={(DOMAIN, f"lock_{lock_id}")},
        manufacturer="Sifely",
        name=alias,
        model=lock_data.get("lockName", "Unknown Model"),
        sw_version=str(lock_data.get("keyboardPwdVersion", "n/a")),
    )
