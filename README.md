# sifely_cloud_custom

You can retrieve the Client ID and Client Secret from
https://app-smart-manager.sifely.com/Login.html


Component	Status
token_manager.py	Manages login + token refresh with caching
__init__.py	Registers platforms and handles setup/unload
sifely.py	Discovers locks and populates devices/entities
lock.py	Creates LockEntity with coordinator updates
sensor.py	Adds battery sensors with % and diagnostic category
const.py	Central config including SUPPORTED_PLATFORMS, KEYLIST_ENDPOINT, etc.

Responsibility	Current Location	Notes
🔐 Authentication & Token Management	token_manager.py	Handles login, refresh, and secure token storage
🔄 Data fetching (lock list)	sifley.py	Uses DataUpdateCoordinator for shared polling
🔒 Lock entities	lock.py	Platform-specific, Home Assistant entity logic
🔋 Sensor entities (battery)	sensor.py	Battery monitoring, with optional presence check
📟 Device registration	device.py	Reusable logic for associating entities with devices


🔐 Authentication Flow
 token_manager.py handles login, token refresh.

 Login URL is POST with query parameters.

 Token extracted from "data.token" in JSON response.

 Refresh token handled using the refresh_token grant type.

🔄 Coordinator (SifelyCoordinator)
 Located in sifely.py.

 Makes POST request to /v3/key/list with correct headers + token.

 Stores lock list in coordinator.data.

 Injected into hass.data[DOMAIN]["coordinator"].

🔧 Platforms
 lock.py reads from coordinator, shows lock state (passageMode).

 sensor.py adds battery sensors only if electricQuantity is present.

 Both use device.py to register DeviceInfo cleanly.

 Each platform calls coordinator.async_add_listener(...).

🔁 Dynamic Refresh
 5-minute refresh interval is configured.

 Manual refresh via entity UI should update data (calls async_update()).

🔧 Setup Logic
 __init__.py uses setup_sifely_coordinator(...) correctly.

 Token manager initialized and stored in hass.data[DOMAIN][entry_id].



