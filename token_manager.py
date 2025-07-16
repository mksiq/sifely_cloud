import logging
from datetime import datetime, timedelta
import aiohttp
import asyncio

from .const import TOKEN_ENDPOINT, REFRESH_ENDPOINT

_LOGGER = logging.getLogger(__name__)


class SifelyTokenManager:
    """Handles login and token management for Sifely Cloud."""

    def __init__(self, client_id, username, password, session: aiohttp.ClientSession):
        self.client_id = client_id
        self.username = username
        self.password = password
        self.session = session

        self.access_token = None
        self.refresh_token = None
        self.token_expiry = datetime.utcnow()

    async def get_token(self):
        now = datetime.datetime.utcnow()
        if self.access_token and self.token_expiry and now < self.token_expiry:
            return self.access_token

        if self.refresh_token:
            try:
                await self.refresh_from_refresh_token()
                return self.access_token
            except Exception:
                _LOGGER.warning("⚠️ Refresh token failed, falling back to full login")

        await self.refresh_token_func()
        return self.access_token

    async def refresh_token_func(self):
        """Login and refresh access token."""
        try:
            _LOGGER.debug("🔐 Requesting Sifely token from: %s", TOKEN_ENDPOINT)

            params = {
                "client_id": self.client_id,
                "username": self.username,
                "password": self.password,
            }

            async with self.session.post(TOKEN_ENDPOINT, params=params, timeout=10) as resp:
                data = await resp.json()
                _LOGGER.debug("🔁 Sifely token response: %s", data)

                if data.get("code") != 200 or "data" not in data:
                    raise Exception(f"Login failed: {data.get('message', 'Unknown error')}")

                self.access_token = data["data"]["token"]
                self.refresh_token = data["data"]["refreshToken"]

                # Assume token is good for 1 hour (can adjust if needed)
                self.token_expiry = datetime.utcnow() + timedelta(seconds=3600)

                _LOGGER.info("✅ Sifely token acquired. Expires in 1 hour.")

        except aiohttp.ClientConnectorError as e:
            _LOGGER.error("❌ Could not connect to Sifely: %s", e)
            raise

        except asyncio.TimeoutError:
            _LOGGER.error("❌ Timeout connecting to Sifely token endpoint.")
            raise

        except Exception as e:
            _LOGGER.exception("❌ Failed to refresh Sifely token")
            raise

    async def refresh_from_refresh_token(self):
        if not self.refresh_token:
            raise ValueError("No refresh token available")

        payload = {
            "client_id": self.client_id,
            "refresh_token": self.refresh_token,
        }

        _LOGGER.debug("🔄 Refreshing Sifely access token using refresh_token")

        try:
            async with self.session.post(REFRESH_ENDPOINT, json=payload) as resp:
                resp.raise_for_status()
                result = await resp.json()
                _LOGGER.debug("🔄 Refresh token response: %s", result)

                self.access_token = result["access_token"]
                self.refresh_token = result["refresh_token"]
                self.token_expiry = datetime.datetime.utcnow() + datetime.timedelta(seconds=result["expires_in"] - 60)

                _LOGGER.info("✅ Sifely token refreshed successfully")
        except Exception as e:
            _LOGGER.exception("❌ Failed to refresh Sifely token")
            raise
