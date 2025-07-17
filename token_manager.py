import logging
from datetime import datetime, timezone, timedelta

from homeassistant.helpers.event import async_call_later

from .const import (
    TOKEN_ENDPOINT,
    REFRESH_ENDPOINT,
    TOKEN_LIFETIME_MINUTES,
    TOKEN_REFRESH_BUFFER_MINUTES,
)

_LOGGER = logging.getLogger(__name__)

class SifelyTokenManager:
    def __init__(self, client_id, email, password, session, hass):
        self.email = email
        self.password = password
        self.client_id = client_id
        self.session = session
        self.hass = hass

        self.access_token = None
        self.refresh_token_value = None
        self.token_expiry = None

        self._refresh_unsub = None

    async def login(self):
        """Login to retrieve initial access and refresh tokens."""
        payload = {
            "client_id": self.client_id,
            "username": self.email,
            "password": self.password,
        }

        _LOGGER.debug("🔐 Requesting Sifely token from: %s", TOKEN_ENDPOINT)

        try:
            async with self.session.post(TOKEN_ENDPOINT, params=payload) as resp:
                resp_json = await resp.json()
                _LOGGER.debug("🔁 Sifely token response: %s", resp_json)

                if resp.status == 200 and "data" in resp_json:
                    data = resp_json["data"]
                    self.access_token = data.get("token")
                    self.refresh_token_value = data.get("refreshToken")
                    expires_in = data.get("expires_in")

                    self._set_token_expiry(expires_in)
                    minutes_until_expiry = (self.token_expiry - datetime.now(timezone.utc)).total_seconds() / 60
                    _LOGGER.info("✅ Sifely token acquired. Expires in %.2f minutes.", minutes_until_expiry)

                    # Schedule refresh
                    self._schedule_token_refresh()
                else:
                    _LOGGER.error("❌ Failed to retrieve token: %s", resp_json)
        except Exception as e:
            _LOGGER.exception("🚨 Exception during Sifely token request: %s", str(e))

    async def refresh_access_token(self):
        """Use the refresh token to obtain a new access token."""
        if not self.refresh_token_value:
            _LOGGER.warning("⚠️ No refresh token available; falling back to full login")
            await self.login()
            return

        payload = {
            "client_id": self.client_id,
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token_value,
        }
        _LOGGER.debug("🔄 Refreshing Sifely access token from: %s", REFRESH_ENDPOINT)

        try:
            async with self.session.post(REFRESH_ENDPOINT, params=payload) as resp:
                resp_json = await resp.json()
                _LOGGER.debug("🔁 Refresh token response: %s", resp_json)

                if resp.status == 200 and "access_token" in resp_json:
                    self.access_token = resp_json.get("access_token")
                    self.refresh_token_value = resp_json.get("refresh_token")
                    expires_in = resp_json.get("expires_in")

                    self._set_token_expiry(expires_in)
                    minutes_until_expiry = (self.token_expiry - datetime.now(timezone.utc)).total_seconds() / 60
                    _LOGGER.info("🔄 Token refreshed successfully. Expires in %.2f minutes.", minutes_until_expiry)

                    # Re-schedule next refresh
                    self._schedule_token_refresh()
                else:
                    _LOGGER.error("❌ Failed to refresh token: %s", resp_json)
        except Exception as e:
            _LOGGER.exception("🚨 Exception during token refresh: %s", str(e))


    def _set_token_expiry(self, expires_in: int = None):
        now = datetime.now(timezone.utc)
        if expires_in is not None:
            # Use actual expires_in value from the API response
            expires = now + timedelta(seconds=expires_in)
            _LOGGER.debug("🕒 Token expiry set using API-provided expires_in: %d seconds", expires_in)
        else:
            # Fallback to default configured duration
            expires = now + timedelta(minutes=TOKEN_LIFETIME_MINUTES)
            _LOGGER.debug("🕒 Token expiry set using default TOKEN_LIFETIME_MINUTES: %d minutes", TOKEN_LIFETIME_MINUTES)

        self.token_expiry = expires


    def _schedule_token_refresh(self):
        if self._refresh_unsub:
            self._refresh_unsub()

        now = datetime.now(timezone.utc)
        delay = (self.token_expiry - timedelta(minutes=TOKEN_REFRESH_BUFFER_MINUTES) - now).total_seconds()
        delay = max(delay, 30)  # Ensure some minimum delay, 30 seconds

        _LOGGER.debug("⏳ Scheduling token refresh in %.2f seconds", delay)

        self._refresh_unsub = async_call_later(self.hass, delay, self._handle_token_refresh)

    async def _handle_token_refresh(self, _):
        _LOGGER.info("🔁 Refreshing token before expiration...")
        await self.refresh_access_token()

    def get_token_expiry_minutes(self) -> int:
        if not self.token_expiry:
            return 0
        return int((self.token_expiry - datetime.now(timezone.utc)).total_seconds() / 60)


    # TODO: Implement logout if needed
    async def async_shutdown(self):
        """Clean up resources when unloading the integration."""
        if self._refresh_unsub:
            self._refresh_unsub()  # Cancel the scheduled callback
            self._refresh_unsub = None
