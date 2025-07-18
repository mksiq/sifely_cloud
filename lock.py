import logging

from homeassistant.components.lock import LockEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN
from .device import async_register_lock_device

_LOGGER = logging.getLogger(__name__)


def create_lock_entities(locks: list[dict], coordinator: DataUpdateCoordinator) -> list[LockEntity]:
    """Create lock entities from Sifely lock data."""
    entities = []
    for lock in locks:
        if lock.get("lockId") is not None:
            entities.append(SifelySmartLock(lock, coordinator))
        else:
            _LOGGER.warning("⚠️ Skipping lock with missing lockId: %s", lock)
    return entities


class SifelySmartLock(LockEntity):
    """Representation of a Sifely Smart Lock."""

    def __init__(self, lock_data: dict, coordinator: DataUpdateCoordinator):
        self.coordinator = coordinator
        self.lock_data = lock_data
        lock_id = lock_data.get("lockId")

        self._attr_name = lock_data.get("lockAlias", "Sifely Lock")
        self._attr_unique_id = f"sifely_lock_{lock_id}" if lock_id else None
        self._attr_device_info = async_register_lock_device(lock_data)

    @property
    def is_locked(self) -> bool | None:
        # Using passageMode: 2 = unlocked, 1 = locked (subject to confirmation)
        passage_mode = self.lock_data.get("passageMode")
        if passage_mode is None:
            return None
        return passage_mode != 2

    async def async_lock(self, **kwargs):
        # TODO: Implement actual lock API call
        _LOGGER.info("🔒 Lock command issued for %s", self.lock_data.get("lockAlias"))

    async def async_unlock(self, **kwargs):
        # TODO: Implement actual unlock API call
        _LOGGER.info("🔓 Unlock command issued for %s", self.lock_data.get("lockAlias"))

    @property
    def available(self):
        return self.lock_data.get("lockId") is not None

    async def async_update(self):
        await self.coordinator.async_request_refresh()

    async def async_added_to_hass(self):
        self.async_on_remove(self.coordinator.async_add_listener(self._handle_coordinator_update))

    def _handle_coordinator_update(self):
        for updated_lock in self.coordinator.data:
            if updated_lock.get("lockId") == self.lock_data.get("lockId"):
                self.lock_data = updated_lock
                break
        self.async_write_ha_state()


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Sifely lock entities."""
    _LOGGER.info("🔐 Setting up Sifely locks")

    coordinator = hass.data[DOMAIN].get("coordinator")
    if not coordinator:
        _LOGGER.warning("⚠️ No coordinator found for Sifely locks")
        return

    entities = create_lock_entities(coordinator.data, coordinator)
    async_add_entities(entities)

    if entities:
        _LOGGER.info("🔐 %d Sifely locks added.", len(entities))
    else:
        _LOGGER.warning("⚠️ No Sifely locks found to set up.")
