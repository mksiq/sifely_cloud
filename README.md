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

