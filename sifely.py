# sifely.py

import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, KEYLIST_ENDPOINT, CONF_APX_NUM_LOCKS
from .token_manager import SifelyTokenManager

_LOGGER = logging.getLogger(__name__)


class SifelyCoordinator(DataUpdateCoordinator):
    """Coordinates updates for Sifely locks."""

    def __init__(
        self,
        hass: HomeAssistant,
        token_manager: SifelyTokenManager,
        config_entry,
    ):
        self.hass = hass
        self.token_manager = token_manager
        self.config_entry = config_entry
        self.session = token_manager.session
        self.login_token = token_manager.get_login_token()
        self.apx_locks = config_entry.options.get(CONF_APX_NUM_LOCKS, 5)

        if not self.login_token:
            raise UpdateFailed("❌ Could not retrieve valid login token.")

        super().__init__(
            hass,
            _LOGGER,
            name="sifely_lock_coordinator",
            update_interval=timedelta(minutes=5),
        )

    async def _async_update_data(self):
        """Fetch lock data from the Sifely API."""
        headers = {
            "Authorization": f"Bearer {self.login_token}",
            "Content-Type": "application/json",
        }
        params = {
            "pageNo": 1,
            "pageSize": self.apx_locks,
        }

        try:
            _LOGGER.debug("📡 Fetching lock list from: %s", KEYLIST_ENDPOINT)
            async with self.session.post(KEYLIST_ENDPOINT, headers=headers, params=params) as resp:
                data = await resp.json()
                _LOGGER.debug("🔑 Lock list response: %s", data)

                if resp.status != 200 or "list" not in data:
                    raise UpdateFailed(f"Unexpected lock list response: {data}")

                return data["list"]

        except Exception as e:
            _LOGGER.exception("🚨 Failed to fetch lock list: %s", str(e))
            raise UpdateFailed(f"Exception fetching locks: {str(e)}")


async def setup_sifely_coordinator(
    hass: HomeAssistant,
    token_manager: SifelyTokenManager,
    config_entry,
) -> SifelyCoordinator:
    """Initialize, refresh, and store the coordinator."""
    coordinator = SifelyCoordinator(hass, token_manager, config_entry)
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})["coordinator"] = coordinator
    return coordinator
