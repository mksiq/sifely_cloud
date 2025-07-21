import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import slugify

from .const import DOMAIN, ENTITY_PREFIX
from .device import async_register_lock_device

_LOGGER = logging.getLogger(__name__)


def create_battery_entities(locks: list[dict], coordinator) -> list[SensorEntity]:
    """Create battery sensor entities for each lock."""
    entities = []
    for lock in locks:
        if lock.get("lockId") is not None:
            entities.append(SifelyBatterySensor(lock, coordinator))
        else:
            _LOGGER.warning("⚠️ Skipping battery sensor for lock with missing lockId: %s", lock)
    return entities


class SifelyBatterySensor(CoordinatorEntity, SensorEntity):
    """Battery level sensor for Sifely Smart Lock."""

    def __init__(self, lock_data: dict, coordinator):
        super().__init__(coordinator)
        self.coordinator = coordinator
        self.lock_data = lock_data

        alias = lock_data.get("lockAlias", "Sifely Lock")
        slug = slugify(alias)
        lock_id = lock_data.get("lockId")

        self._attr_name = f"{ENTITY_PREFIX.capitalize()} Battery {alias}"  # e.g., "Sifely Battery Front Door"
        self._attr_unique_id = f"{ENTITY_PREFIX}_battery_{slug}_{lock_id}"
        self._attr_device_class = "battery"
        self._attr_native_unit_of_measurement = "%"
        self._attr_state_class = "measurement"
        self._attr_device_info = async_register_lock_device(lock_data)

    @property
    def native_value(self) -> int | None:
        """Return the current battery level."""
        lock_id = self.lock_data.get("lockId")
        details = self.coordinator.details_data.get(lock_id)
        if not details:
            return None
        return details.get("electricQuantity")

    @property
    def available(self):
        """Battery sensor is only available if lockId is known and battery info has been fetched."""
        lock_id = self.lock_data.get("lockId")
        return lock_id is not None and lock_id in self.coordinator.details_data


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up battery sensors."""
    _LOGGER.info("🔋 Setting up Sifely battery sensors")

    coordinator = hass.data[DOMAIN].get("coordinator")
    if not coordinator:
        _LOGGER.warning("⚠️ No coordinator found for battery sensors")
        return

    entities = create_battery_entities(coordinator.data, coordinator)
    async_add_entities(entities)

    if entities:
        _LOGGER.info("🔋 %d Sifely battery sensors added.", len(entities))
    else:
        _LOGGER.warning("⚠️ No battery sensors found to set up.")
