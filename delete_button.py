# button.py

import logging
from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import slugify

from .const import DOMAIN, ENTITY_PREFIX, HISTORY_DISPLAY_LIMIT
from .device import async_register_lock_device

_LOGGER = logging.getLogger(__name__)


# async def async_setup_entry(
#     hass: HomeAssistant,
#     config_entry: ConfigEntry,
#     async_add_entities: AddEntitiesCallback,
# ) -> None:
#     """Set up Sifely refresh buttons for lock history."""
#     _LOGGER.info("🆕 Setting up Sifely history refresh buttons")

#     coordinator = hass.data[DOMAIN].get("coordinator")
#     if not coordinator:
#         _LOGGER.warning("⚠️ No coordinator found for buttons")
#         return

#     buttons = []
#     for lock in coordinator.data:
#         if lock.get("lockId"):
#             buttons.append(SifelyHistoryRefreshButton(lock, coordinator))

#     async_add_entities(buttons)

#     if buttons:
#         _LOGGER.info("✅ %d history refresh buttons added", len(buttons))
#     else:
#         _LOGGER.warning("⚠️ No buttons found to set up")


# class SifelyHistoryRefreshButton(ButtonEntity):
#     """Button to manually fetch and display lock history."""

#     RECORD_TYPE_MAP = {
#         -5: "Face",
#         -4: "QR Code",
#         4: "Keyboard",
#         7: "IC Card",
#         8: "Fingerprint",
#         55: "Remote",
#     }

#     def __init__(self, lock_data, coordinator):
#         self.coordinator = coordinator
#         self.lock_data = lock_data

#         alias = lock_data.get("lockAlias", "Sifely Lock")
#         slug = slugify(alias)
#         lock_id = lock_data.get("lockId")

#         self.lock_id = lock_id
#         self._attr_name = f"{ENTITY_PREFIX.capitalize()} Refresh History {alias}"
#         self._attr_unique_id = f"{ENTITY_PREFIX}_refresh_history_button_{slug}_{lock_id}"
#         self._attr_icon = "mdi:refresh"
#         self._attr_device_info = async_register_lock_device(lock_data)
#         self._attr_extra_state_attributes = {}

#     async def async_press(self) -> None:
#         """Handle button press: fetch and store history as attributes."""
#         _LOGGER.info("📥 Manual refresh: fetching history for lock %s", self.lock_id)
#         history = await self.coordinator.async_query_lock_history(self.lock_id)

#         if not history:
#             _LOGGER.info("📭 No history found for lock %s", self.lock_id)
#             self._attr_extra_state_attributes = {"history": "No recent activity"}
#             return

#         attr_map = {}

#         for i, entry in enumerate(history[:HISTORY_DISPLAY_LIMIT]):
#             user = entry.get("username", "Unknown")
#             ts = entry.get("lockDate")
#             record_type = entry.get("recordType", "N/A")
#             success = entry.get("success", -1)

#             method = self.RECORD_TYPE_MAP.get(record_type, f"Type {record_type}")
#             status = "✅" if success == 1 else "❌"

#             try:
#                 from datetime import datetime, timezone
#                 dt = datetime.fromtimestamp(ts / 1000, tz=timezone.utc).astimezone()
#                 ts_str = dt.strftime("%Y-%m-%d %H:%M:%S")
#             except Exception:
#                 ts_str = str(ts)

#             attr_map[f"entry_{i+1}"] = f"{ts_str}: {user} via {method} — {status}"

#         self._attr_extra_state_attributes = attr_map
#         _LOGGER.debug("📝 History attributes updated for lock %s", self.lock_id)
