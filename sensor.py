import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.entity import EntityCategory

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


def create_battery_entities(locks: list[dict], coordinator: DataUpdateCoordinator) -> list[SensorEntity]:
    entities = []
    for lock in locks:
        battery = lock.get("electricQuantity")
        if battery is not None:
            entities.append(SifelyBatterySensor(lock, coordinator))
    return entities


class SifelyBatterySensor(SensorEntity):
    def __init__(self, lock_data: dict, coordinator: DataUpdateCoordinator):
        self.coordinator = coordinator
        self.lock_data = lock_data
        self._attr_name = f"{lock_data.get('lockAlias', 'Sifely Lock')} Battery"
        self._attr_unique_id = f"sifely_battery_{lock_data.get('lockId')}"
        self._attr_native_unit_of_measurement = "%"
        self._attr_device_class = "battery"
        self._attr_state_class = "measurement"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self):
        return self.lock_data.get("electricQuantity")

    @property
    def available(self):
        return self.lock_data.get("electricQuantity") is not None

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
    """Set up Sifely battery sensors."""
    _LOGGER.info("🔋 Setting up Sifely battery sensors")

    coordinator = hass.data[DOMAIN].get("coordinator")
    if not coordinator:
        _LOGGER.warning("⚠️ No coordinator found for Sifely battery sensors")
        return

    entities = create_battery_entities(coordinator.data, coordinator)
    async_add_entities(entities)
    _LOGGER.info("🔋 %d Sifely battery sensors added.", len(entities))
