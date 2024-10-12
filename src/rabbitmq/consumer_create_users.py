from typing import Dict

from aiohttp import ClientSession
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import RMQ_USER, RMQ_PASSWORD, RMQ_HOST, RMQ_PORT, RMQ_VHOST
from src.rabbitmq.consumer import start_consumer
from loguru import logger

from src.users.exceptions import UserAlreadyExistsException, WidgetNotFoundException
from src.users.schemas import UserResponse
from src.users.services import check_user_exists, get_client_secret_redirect_url, create_user
from src.users.tokens_init import initialize_token_manager


async def process_get_settings_user(message: dict, session: AsyncSession):
    """Получаем code, secret, client_id чтобы создать пользователя в бд."""

    subdomain = message.get("subdomain")
    client_id = message.get("client_id")
    code = message.get("code")

    if not subdomain or not client_id or not code:
        logger.error("Missing required parameters in message: subdomain, client_id, or code")
        raise HTTPException(status_code=400, detail="Missing required parameters: subdomain, client_id, or code")

    try:
        # Проверяем, существует ли пользователь
        await check_user_exists(client_id, subdomain, session)

        # Получаем client_secret и redirect_url для данного клиента
        client_secret, redirect_url = await get_client_secret_redirect_url(client_id, session)

        # Инициализируем токен-менеджер для получения токенов
        access_token, refresh_token = await initialize_token_manager(
            client_id, client_secret, subdomain, code, redirect_url
        )

        # Создаем нового пользователя в базе данных
        new_user = await create_user(
            client_id, subdomain, access_token, refresh_token, session
        )

        logger.info(f"User created successfully: {new_user.id}")

        # Формируем ответ, аналогичный response модели UserResponse
        return UserResponse(
            id=new_user.id,
            client_id=new_user.client_id,
            subdomain=new_user.subdomain
        )

    except UserAlreadyExistsException:
        logger.error(f"User with client_id: {client_id} and subdomain: {subdomain} already exists")
        raise HTTPException(status_code=409, detail="User already exists")

    except WidgetNotFoundException:
        logger.error(f"Widget for client_id: {client_id} not found")
        raise HTTPException(status_code=404, detail="Widget not found")

    except Exception as e:
        logger.exception(f"Error processing user creation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def start_token_add_user_consumer():
    connection_url = (
        f"amqp://{RMQ_USER}:{RMQ_PASSWORD}@{RMQ_HOST}:{RMQ_PORT}/{RMQ_VHOST}"
    )
    logger.info(f"Connecting to RabbitMQ at {connection_url}")
    print(f"Connecting to RabbitMQ at {connection_url}")

    await start_consumer(
        "token_add_user", connection_url, process_get_settings_user
    )

    logger.info("Consumer for 'leads_allocate_get_users' started.")

