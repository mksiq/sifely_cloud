import logging
from datetime import datetime, timezone, timedelta

from homeassistant.helpers.event import async_call_later

from .const import (
    TOKEN_ENDPOINT,
    REFRESH_ENDPOINT,
    TOKEN_REFRESH_BUFFER_MINUTES,
)

_LOGGER = logging.getLogger(__name__)

class SifelyTokenManager:
    def __init__(self, client_id, email, password, session, hass, config_entry):
        self.client_id = client_id
        self.email = email
        self.password = password
        self.session = session
        self.hass = hass
        self.config_entry = config_entry

        self.login_token = None  # Used for device discovery
        self.access_token = None  # Used for general API requests
        self.refresh_token_value = None
        self.token_expiry = None

        self._refresh_unsub = None

    async def initialize(self):
        """Entry point on integration boot."""
        self._load_stored_tokens()

        if self._is_token_valid():
            _LOGGER.info("✅ Using cached token. Expires at: %s", self.token_expiry)
            self._schedule_token_refresh()
        else:
            _LOGGER.info("🔐 No valid token found. Performing login...")
            await self._perform_login()
            await self._perform_token_refresh()

    def _load_stored_tokens(self):
        opts = self.config_entry.options
        self.login_token = opts.get("login_token")
        self.access_token = opts.get("access_token")
        self.refresh_token_value = opts.get("refresh_token")
        expiry_ts = opts.get("token_expiry")

        if expiry_ts:
            self.token_expiry = datetime.fromisoformat(expiry_ts)

    def _is_token_valid(self):
        if not self.access_token or not self.token_expiry:
            return False
        return datetime.now(timezone.utc) < self.token_expiry

    async def _perform_login(self):
        payload = {
            "client_id": self.client_id,
            "username": self.email,
            "password": self.password,
        }

        _LOGGER.debug("🔐 Requesting Sifely login from: %s", TOKEN_ENDPOINT)

        try:
            async with self.session.post(TOKEN_ENDPOINT, params=payload) as resp:
                resp_json = await resp.json()
                _LOGGER.debug("🔁 Login response: %s", resp_json)

                if resp.status == 200 and "data" in resp_json:
                    data = resp_json["data"]
                    self.login_token = data.get("token")
                    self.refresh_token_value = data.get("refreshToken")
                else:
                    raise Exception(f"Login failed: {resp_json}")
        except Exception as e:
            _LOGGER.exception("🚨 Exception during login: %s", str(e))
            raise

    async def _perform_token_refresh(self):
        payload = {
            "client_id": self.client_id,
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token_value,
        }
        _LOGGER.debug("🔄 Refreshing token from: %s", REFRESH_ENDPOINT)

        try:
            async with self.session.post(REFRESH_ENDPOINT, params=payload) as resp:
                resp_json = await resp.json()
                _LOGGER.debug("🔁 Refresh token response: %s", resp_json)

                if resp.status == 200 and "access_token" in resp_json:
                    self.access_token = resp_json.get("access_token")
                    self.refresh_token_value = resp_json.get("refresh_token")
                    expires_in = resp_json.get("expires_in")
                    self._set_token_expiry(expires_in)
                    await self._store_token()
                    _LOGGER.info("🔄 Token refreshed. Expires at: %s", self.token_expiry)
                    self._schedule_token_refresh()
                else:
                    raise Exception(f"Refresh failed: {resp_json}")
        except Exception as e:
            _LOGGER.exception("🚨 Exception during token refresh: %s", str(e))
            await self._perform_login()
            await self._perform_token_refresh()

    def _set_token_expiry(self, expires_in):
        now = datetime.now(timezone.utc)
        self.token_expiry = now + timedelta(seconds=expires_in)

    def _schedule_token_refresh(self):
        if self._refresh_unsub:
            self._refresh_unsub()

        now = datetime.now(timezone.utc)
        delay = (self.token_expiry - timedelta(minutes=TOKEN_REFRESH_BUFFER_MINUTES) - now).total_seconds()
        delay = max(delay, 30)

        _LOGGER.debug("⏳ Scheduling token refresh in %.2f seconds", delay)
        self._refresh_unsub = async_call_later(self.hass, delay, self._handle_token_refresh)

    async def _handle_token_refresh(self, _):
        _LOGGER.info("🔁 Token refresh scheduled task running...")
        await self._perform_token_refresh()

    async def _store_token(self):
        opts = dict(self.config_entry.options)
        opts.update({
            "login_token": self.login_token,
            "access_token": self.access_token,
            "refresh_token": self.refresh_token_value,
            "token_expiry": self.token_expiry.isoformat(),
        })
        self.hass.config_entries.async_update_entry(self.config_entry, options=opts)

    async def async_shutdown(self):
        if self._refresh_unsub:
            self._refresh_unsub()
            self._refresh_unsub = None

    def get_login_token(self):
        return self.login_token

    def get_access_token(self):
        return self.access_token
