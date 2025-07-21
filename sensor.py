import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import slugify
from datetime import datetime, timezone

from .const import DOMAIN, ENTITY_PREFIX, HISTORY_DISPLAY_LIMIT
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

def create_history_entities(locks: list[dict], coordinator) -> list[SensorEntity]:
    """Create lock history sensor entities for each lock."""
    entities = []
    for lock in locks:
        if lock.get("lockId") is not None:
            entities.append(SifelyLockHistorySensor(lock, coordinator))
        else:
            _LOGGER.warning("⚠️ Skipping history sensor for lock with missing lockId: %s", lock)
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


class SifelyLockHistorySensor(CoordinatorEntity, SensorEntity):
    """Sensor to display recent lock activity as text."""

    RECORD_TYPE_MAP = {
        -5: "Face",
        -4: "QR Code",
        4: "Keyboard",
        7: "IC Card",
        8: "Fingerprint",
        55: "Remote",
    }

    def __init__(self, lock_data: dict, coordinator):
        super().__init__(coordinator)
        self.coordinator = coordinator
        self.lock_data = lock_data

        alias = lock_data.get("lockAlias", "Sifely Lock")
        slug = slugify(alias)
        lock_id = lock_data.get("lockId")

        self.lock_id = lock_id
        self.slug = slug

        self._attr_name = f"{ENTITY_PREFIX.capitalize()} History {alias}"
        self._attr_unique_id = f"{ENTITY_PREFIX}_history_{slug}_{lock_id}"
        self._attr_icon = "mdi:history"
        self._attr_device_info = async_register_lock_device(lock_data)
        self._attr_native_value = None
        self._attr_extra_state_attributes = {}

    async def async_update(self):
        """Fetch latest lock history from coordinator."""
        history = await self.coordinator.async_query_lock_history(self.lock_id)

        if not history:
            self._attr_native_value = "No recent activity"
            self._attr_extra_state_attributes = {}
            return

        # Create a summary string (last user, time, type)
        lines = []
        attr_map = {}

        for i, entry in enumerate(history[:HISTORY_DISPLAY_LIMIT]):
            user = entry.get("username", "Unknown")
            ts = entry.get("lockDate")
            record_type = entry.get("recordType", "N/A")
            success = entry.get("success", -1)

            # Map record type to readable name
            method = self.RECORD_TYPE_MAP.get(record_type, f"Type {record_type}")
            success_text = "✅ Success" if success == 1 else "❌ Failed"

            try:
                dt = datetime.fromtimestamp(ts / 1000, tz=timezone.utc).astimezone()
                formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                formatted_time = str(ts)

            line = f"{formatted_time}: {user} via {method} — {success_text}"
            lines.append(line)
            attr_map[f"entry_{i+1}"] = line

        self._attr_native_value = lines[0] if lines else "No recent activity"
        self._attr_extra_state_attributes = attr_map



async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Sifely sensors (battery + history)."""
    _LOGGER.info("🔋 Setting up Sifely sensors")

    coordinator = hass.data[DOMAIN].get("coordinator")
    if not coordinator:
        _LOGGER.warning("⚠️ No coordinator found for sensors")
        return

    battery_entities = create_battery_entities(coordinator.data, coordinator)
    history_entities = create_history_entities(coordinator.data, coordinator)

    all_entities = battery_entities + history_entities
    async_add_entities(all_entities)

    if battery_entities:
        _LOGGER.info("🔋 %d battery sensors added.", len(battery_entities))
    if history_entities:
        _LOGGER.info("📜 %d history sensors added.", len(history_entities))
    if not all_entities:
        _LOGGER.warning("⚠️ No sensors found to set up.")

