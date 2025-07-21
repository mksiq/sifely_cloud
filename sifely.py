# sifely.py (Stable version with persistent polling, one-time lock fetch, and robust error handling)

import logging
import json
from datetime import datetime, timezone, timedelta

from homeassistant.util import dt as dt_util
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    KEYLIST_ENDPOINT,
    LOCK_DETAIL_ENDPOINT,
    CONF_APX_NUM_LOCKS,
    DETAILS_UPDATE_INTERVAL,
    STATE_QUERY_INTERVAL,
    QUERY_STATE_ENDPOINT,
)
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
        self.access_token = token_manager.access_token
        self.apx_locks = config_entry.options.get(CONF_APX_NUM_LOCKS, 5)

        if not self.access_token:
            raise UpdateFailed("❌ Could not retrieve valid login token.")

        self.last_details_update = datetime.min.replace(tzinfo=timezone.utc)
        self.lock_list = []
        self.details_data = {}
        self.open_state_data = {}

        super().__init__(
            hass,
            _LOGGER,
            name="sifely_lock_coordinator",
            # update_interval is disabled; polling is done manually via async_track_time_interval
        )

    async def _async_update_data(self):
        """Disabled auto-update mechanism (we handle it manually)."""
        return self.lock_list

    async def async_fetch_lock_list(self):
        """Get lock data from the Sifely API."""
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        params = {
            "pageNo": 1,
            "pageSize": self.apx_locks,
        }

        try:
            _LOGGER.debug("📡 Fetching lock list from: %s", KEYLIST_ENDPOINT)
            async with self.session.post(KEYLIST_ENDPOINT, headers=headers, params=params) as resp:
                text = await resp.text()
                _LOGGER.debug("🔑 Lock list raw response: %s", text)

                try:
                    data = json.loads(text)
                except Exception as e:
                    raise UpdateFailed(f"Failed to parse lock list response: {e}")

                if resp.status != 200 or "list" not in data:
                    raise UpdateFailed(f"Unexpected lock list response: {data}")

                locks = data["list"]
                self.lock_list = locks
                _LOGGER.info("✅ Fetched %d locks", len(locks))
                return locks

        except Exception as e:
            _LOGGER.exception("🚨 Failed to fetch lock list: %s", str(e))
            raise UpdateFailed(f"Exception fetching locks: {str(e)}")

    async def async_query_open_state(self):
        """Query open/locked state for each lock and store in self.open_state_data."""
        if not self.lock_list:
            _LOGGER.debug("⏩ Skipping open state polling: lock list not available")
            return

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        for lock in self.lock_list:
            lock_id = lock.get("lockId")
            if not lock_id:
                _LOGGER.warning("🔑 Skipping lock with missing lockId: %s", lock)
                continue

            url = f"{QUERY_STATE_ENDPOINT}?lockId={lock_id}"
            try:
                async with self.session.get(url, headers=headers) as resp:
                    text = await resp.text()
                    _LOGGER.debug("🔒 Open state response for %s: %s", lock_id, text)

                    try:
                        data = json.loads(text)

                        if resp.status == 200:
                            # Case 1: Full format
                            if "code" in data:
                                if data.get("code") == 200:
                                    self.open_state_data[lock_id] = data.get("data", {}).get("state")
                                elif data.get("code") == -3003:
                                    _LOGGER.debug("⏳ Gateway busy when querying state for %s. Will retry.", lock_id)
                                else:
                                    _LOGGER.warning("⚠️ Unexpected open state for %s: %s", lock_id, data)

                            # Case 2: Direct state
                            elif "state" in data:
                                self.open_state_data[lock_id] = data.get("state")
                            else:
                                _LOGGER.warning("⚠️ Unknown open state format for %s: %s", lock_id, data)
                        else:
                            _LOGGER.warning("⚠️ HTTP %d when fetching state for %s: %s", resp.status, lock_id, text)

                    except Exception as e:
                        _LOGGER.warning("❌ Failed to parse open state for %s: %s", lock_id, e)

            except Exception as e:
                _LOGGER.warning("🚫 Failed to fetch open state for %s: %s", lock_id, e)

    async def async_query_lock_details(self):
        """Query detailed lock info for each lock and store in self.details_data."""
        if not self.lock_list:
            _LOGGER.debug("⏩ Skipping lock detail polling: lock list not available")
            return

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        for lock in self.lock_list:
            lock_id = lock.get("lockId")
            if not lock_id:
                _LOGGER.warning("🔑 Skipping lock with missing lockId: %s", lock)
                continue

            url = f"{LOCK_DETAIL_ENDPOINT}?lockId={lock_id}"
            try:
                async with self.session.get(url, headers=headers) as resp:
                    text = await resp.text()
                    _LOGGER.debug("🔍 Lock detail response for %s: %s", lock_id, text)

                    try:
                        data = json.loads(text)

                        if resp.status == 200:
                            # Case 1: Standard format
                            if "code" in data:
                                if data.get("code") == 200:
                                    self.details_data[lock_id] = data.get("data", {})
                                elif data.get("code") == -3003:
                                    _LOGGER.debug("⏳ Gateway busy when querying details for %s. Will retry.", lock_id)
                                else:
                                    _LOGGER.warning("⚠️ Unexpected lock detail for %s: %s", lock_id, data)

                            # Case 2: Direct dict fallback
                            elif "lockId" in data:
                                self.details_data[lock_id] = data
                            else:
                                _LOGGER.warning("⚠️ Unknown lock detail format for %s: %s", lock_id, data)
                        else:
                            _LOGGER.warning("⚠️ HTTP %d when fetching details for %s: %s", resp.status, lock_id, text)

                    except Exception as e:
                        _LOGGER.warning("❌ Failed to parse lock detail for %s: %s", lock_id, e)

            except Exception as e:
                _LOGGER.warning("🚫 Failed to fetch lock detail for %s: %s", lock_id, e)


async def setup_sifely_coordinator(
    hass: HomeAssistant,
    token_manager: SifelyTokenManager,
    config_entry,
) -> SifelyCoordinator:
    """Initialize, refresh, and store the coordinator."""
    coordinator = SifelyCoordinator(hass, token_manager, config_entry)

    # 📡 Step 1: Fetch initial lock list
    locks = await coordinator.async_fetch_lock_list()
    coordinator.data = locks  # 🔥 Set initial data for entities

    # 🔋 Step 2: Immediately fetch lock details (so battery sensors are ready)
    await coordinator.async_query_lock_details()

    # 💾 Register the coordinator globally
    hass.data.setdefault(DOMAIN, {})["coordinator"] = coordinator

    # ⏱️ Step 3: Schedule ongoing polling for lock deatails and open state
    async def _run_lock_details(now):
        _LOGGER.debug("⏱️ Scheduled task: Fetching lock details")
        await coordinator.async_query_lock_details()

    async def _run_open_state(now):
        _LOGGER.debug("⏱️ Scheduled task: Fetching open/closed state")
        await coordinator.async_query_open_state()

    async_track_time_interval(hass, _run_lock_details, timedelta(seconds=DETAILS_UPDATE_INTERVAL))
    async_track_time_interval(hass, _run_open_state, timedelta(seconds=STATE_QUERY_INTERVAL))

    return coordinator
