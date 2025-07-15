# sifely_api.py
import aiohttp
import logging
from .const import TOKEN_ENDPOINT
from .token_manager import save_token

_LOGGER = logging.getLogger(__name__)

async def get_token(email, password, client_id, client_secret):
    payload = {
        "email": email,
        "password": password,
        "clientId": client_id,
        "clientSecret": client_secret
    }

    headers = {
        "Content-Type": "application/json"
    }

    _LOGGER.debug("Requesting token from Sifely API...")
    _LOGGER.debug(f"Payload: {payload}")

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(TOKEN_ENDPOINT, json=payload, headers=headers) as resp:
                _LOGGER.debug(f"Response status: {resp.status}")
                text = await resp.text()
                _LOGGER.debug(f"Raw response text: {text}")

                if resp.status != 200:
                    _LOGGER.error("Token request failed with status %s", resp.status)
                    return None

                data = await resp.json()
                save_token(data)
                _LOGGER.info("Token successfully retrieved and saved.")
                return data
        except Exception as e:
            _LOGGER.exception(f"Exception while retrieving token: {e}")
            return None
