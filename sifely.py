import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, KEYLIST_ENDPOINT, CONF_APX_NUM_LOCKS
from .token_manager import SifelyTokenManager
from .lock import create_lock_entities

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Sifely lock entities."""
    _LOGGER.info("🔐 Setting up Sifely platform for locks")

    token_manager: SifelyTokenManager = hass.data[DOMAIN][config_entry.entry_id]
    login_token = token_manager.get_login_token()

    if not login_token:
        _LOGGER.error("❌ Cannot fetch login token from token manager.")
        return

    session = token_manager.session
    apx_locks = config_entry.options.get(CONF_APX_NUM_LOCKS, 5)

    headers = {
        "Authorization": f"Bearer {login_token}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    payload = {
        "keyRight": 1,
        "groupId": 0,
        "pageNo": 1,
        "pageSize": apx_locks,
    }

    async def async_update_data():
        try:
            async with session.post(KEYLIST_ENDPOINT, data=payload, headers=headers) as resp:
                data = await resp.json()
                _LOGGER.debug("🔑 Lock list response: %s", data)

                if resp.status != 200 or "data" not in data or "list" not in data["data"]:
                    raise UpdateFailed(f"Failed to retrieve lock list: {data}")

                return data["data"]["list"]
        except Exception as e:
            raise UpdateFailed(f"Exception while fetching lock list: {str(e)}")

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="sifely_locks",
        update_method=async_update_data,
        update_interval=timedelta(minutes=5),
    )

    await coordinator.async_config_entry_first_refresh()

    entities = create_lock_entities(coordinator.data, coordinator)
    async_add_entities(entities)
    _LOGGER.info("🔐 %d Sifely locks added.", len(entities))
