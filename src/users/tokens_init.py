from typing import Tuple
from loguru import logger

import aiohttp
from fastapi import HTTPException


async def initialize_token_manager(
        client_id: str, client_secret: str, subdomain: str, code: str, redirect_uri: str
) -> Tuple[str, str]:
    """Первое получение access токена и refresh"""

    url = f"https://{subdomain}.amocrm.ru/oauth2/access_token"
    headers = {
        "Content-Type": "application/json",
    }

    body = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
    }

    try:
        async with aiohttp.ClientSession() as client_session:
            async with client_session.post(url, json=body, headers=headers) as response:
                # Проверяем статус ответа
                response.raise_for_status()

                data = await response.json()
                access_token = data.get("access_token")
                refresh_token = data.get("refresh_token")

                if not access_token or not refresh_token:
                    logger.error(f"Failed to receive tokens from the server")
                    raise HTTPException(
                        status_code=500,
                        detail="Tokens not found in server response"
                    )

                return access_token, refresh_token

    except aiohttp.ClientError as client_err:
        logger.error(f"Network error while getting tokens for {subdomain}: Error {client_err}")
        raise HTTPException(status_code=502, detail="Bad Gateway - Error connecting to AmoCRM")

    except Exception as e:
        logger.exception(
            f"Error when receiving access and refresh token for {subdomain}:{client_id}. Error: {e}"
        )
        raise HTTPException(
            status_code=500,
            detail="Error when receiving access and refresh token."
        )


async def get_new_tokens(subdomain: str, refresh_token: str, client_id: str, client_secret: str) -> Tuple[str, str]:
    """Обновление токенов с помощью refresh_token"""

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
                # Проверяем статус ответа
                response.raise_for_status()

                data = await response.json()
                new_access_token = data.get("access_token")
                new_refresh_token = data.get("refresh_token")

                if not new_access_token or not new_refresh_token:
                    logger.error(f"Failed to receive NEW tokens from the server")
                    raise HTTPException(
                        status_code=500,
                        detail="New tokens not found in server response"
                    )

                return new_access_token, new_refresh_token

    except aiohttp.ClientError as client_err:
        logger.error(f"Network error while getting tokens for {subdomain}: Error {client_err}")
        raise HTTPException(status_code=502, detail="Bad Gateway - Error connecting to AmoCRM")

    except Exception as e:
        logger.exception(
            f"Error when receiving NEW access and refresh token for {subdomain}:{client_id}. Error: {e}"
        )
        raise HTTPException(
            status_code=500,
            detail="Error when receiving NEW access and refresh token."
        )
