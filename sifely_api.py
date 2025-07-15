# sifely_api.py
import aiohttp
import asyncio
from .const import TOKEN_ENDPOINT
from .token_manager import save_token

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

    async with aiohttp.ClientSession() as session:
        async with session.post(TOKEN_ENDPOINT, json=payload, headers=headers) as resp:
            if resp.status != 200:
                raise Exception(f"Failed to get token: {resp.status}")
            data = await resp.json()
            save_token(data)
            return data
