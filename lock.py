import logging
from homeassistant.components.lock import LockEntity
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


def create_lock_entities(config_entry, coordinator):
    """Create lock entities for each Sifely lock."""
    entities = []

    for lock in coordinator.locks:
        lock_id = lock.get("lockId")
        if not lock_id:
            continue

        entity = SifelyLockEntity(config_entry, coordinator, lock)
        entities.append(entity)

    return entities


class SifelyLockEntity(LockEntity):
    def __init__(self, config_entry, coordinator, lock_data):
        self._config_entry = config_entry
        self._coordinator = coordinator
        self._lock_data = lock_data
        self._lock_id = str(lock_data["lockId"])
        self._lock_alias = lock_data.get("lockAlias", f"Sifely Lock {self._lock_id}")

        self._attr_unique_id = f"{DOMAIN}_{self._lock_id}_lock"
        self._attr_name = self._lock_alias
        self._attr_is_locked = self._get_initial_lock_state()

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._lock_id)},
            name=self._lock_alias,
            manufacturer="Sifely",
            model=self._lock_data.get("lockName"),
        )

    def _get_initial_lock_state(self):
        passage_mode = self._lock_data.get("passageMode")
        if passage_mode == 2:  # Unlocked
            return False
        elif passage_mode == 1:  # Locked
            return True
        return None

    async def async_lock(self, **kwargs):
        _LOGGER.info("🔒 Locking %s", self._lock_alias)
        await self._send_lock_command(lock=True)

    async def async_unlock(self, **kwargs):
        _LOGGER.info("🔓 Unlocking %s", self._lock_alias)
        await self._send_lock_command(lock=False)

    async def _send_lock_command(self, lock: bool):
        # TODO: Implement lock/unlock API call using lockId and token
        action = "lock" if lock else "unlock"
        _LOGGER.debug("[SIMULATED] Would send '%s' command to lockId=%s", action, self._lock_id)
        self._attr_is_locked = lock
        self.async_write_ha_state()

    async def async_update(self):
        await self._coordinator.async_request_refresh()
        self._attr_is_locked = self._get_initial_lock_state()
