from typing import Tuple

import aiohttp
from amocrm.v2 import tokens


async def initialize_token_manager(
        client_id: str, client_secret: str, subdomain: str, code: str, redirect_url: str
) -> Tuple[str, str]:
    """Инициализация менеджера токенов. Первое получение access токена и refresh"""

    storage = tokens.MemoryTokensStorage()
    tokens.default_token_manager(
        client_id=client_id,
        client_secret=client_secret,
        subdomain=subdomain,
        redirect_url=redirect_url,
        storage=storage,
    )

    tokens.default_token_manager.init(code=code, skip_error=False)

    access_token = tokens.default_token_manager.get_access_token()
    refresh_token = tokens.default_token_manager._storage.get_refresh_token()

    if not (access_token and refresh_token):
        raise ValueError("Tokens didn't create")

    return access_token, refresh_token


async def get_new_tokens(subdomain: str, refresh_token: str, client_id: str, client_secret: str) -> Tuple[str, str]:
    """Получение новых токенов с помощью refresh_token"""

    url = f"https://{subdomain}.amocrm.ru/oauth2/access_token"
    headers = {
        "Content-Type": "application/json",
    }
    body = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }

    try:
        async with aiohttp.ClientSession() as client_session:
            async with client_session.post(url, json=body, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    new_access_token = data.get("access_token")
                    new_refresh_token = data.get("refresh_token")

                    if not new_access_token and not new_refresh_token:
                        raise ValueError("Missing tokens in response")

                    return new_access_token, new_refresh_token
                else:
                    error_message = await response.text()
                    raise ValueError(f"Failed to fetch tokens: {error_message}")

    except aiohttp.ClientError as e:
        raise ValueError(f"HTTP client error: {e}")
    except Exception as e:
        raise ValueError(f"Unexpected error: {e}")
