import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.entity import EntityCategory
from homeassistant.util import slugify

from .const import DOMAIN, ENTITY_PREFIX
from .device import async_register_lock_device

_LOGGER = logging.getLogger(__name__)


def create_battery_entities(locks: list[dict], coordinator: DataUpdateCoordinator) -> list[SensorEntity]:
    """Create battery sensors for Sifely locks with battery info."""
    entities = []
    for lock in locks:
        battery = lock.get("electricQuantity")
        lock_id = lock.get("lockId")

        if battery is not None and lock_id is not None:
            entities.append(SifelyBatterySensor(lock, coordinator))
        else:
            _LOGGER.debug(
                "⏭️ Skipping battery sensor creation for lock (missing battery or lockId): %s", lock.get("lockAlias", "Unknown")
            )

    return entities


class SifelyBatterySensor(SensorEntity):
    """Battery level sensor for a Sifely lock."""

    def __init__(self, lock_data: dict, coordinator: DataUpdateCoordinator):
        self.coordinator = coordinator
        self.lock_data = lock_data

        lock_alias = lock_data.get("lockAlias", "Sifely Lock")
        lock_id = lock_data.get("lockId")

        slug = slugify(lock_alias)
        self._attr_name = f"{lock_alias} Battery"
        self._attr_unique_id = f"{ENTITY_PREFIX}_battery_{lock_id}" if lock_id else None
        self._attr_entity_id = f"sensor.{ENTITY_PREFIX}_{slug}_battery"
        self._attr_native_unit_of_measurement = "%"
        self._attr_device_class = "battery"
        self._attr_state_class = "measurement"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        self._attr_device_info = async_register_lock_device(lock_data)

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
        """Update lock data from coordinator and refresh HA state."""
        current_id = self.lock_data.get("lockId")
        for updated_lock in self.coordinator.data:
            if updated_lock.get("lockId") == current_id:
                self.lock_data = updated_lock
                break
        self.async_write_ha_state()


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Sifely battery sensors from a config entry."""
    _LOGGER.info("🔋 Setting up Sifely battery sensors")

    coordinator = hass.data[DOMAIN].get("coordinator")
    if not coordinator:
        _LOGGER.warning("⚠️ No coordinator found for Sifely battery sensors")
        return

    entities = create_battery_entities(coordinator.data, coordinator)
    async_add_entities(entities)

    if entities:
        _LOGGER.info("🔋 %d Sifely battery sensors added.", len(entities))
    else:
        _LOGGER.warning("⚠️ No battery sensors created (none reported battery or lockId)")
