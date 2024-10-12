from fastapi import HTTPException
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import RMQ_USER, RMQ_HOST, RMQ_PORT, RMQ_VHOST, RMQ_PASSWORD
from src.rabbitmq.consumer import start_consumer
from src.users.exceptions import UserNotFoundException
from src.users.schemas import TokensResponse
from src.users.services import get_tokens_from_db


async def process_get_tokens_message(message: dict, session: AsyncSession):
    """Обрабатываем запрос на получение токенов пользователя из базы данных."""

    client_id = message.get("client_id")
    subdomain = message.get("subdomain")

    if not client_id or not subdomain:
        logger.error("Missing required parameters in message: client_id or subdomain")
        raise HTTPException(status_code=400, detail="Missing required parameters: client_id or subdomain")

    try:
        # Получаем токены пользователя из базы данных
        tokens = await get_tokens_from_db(subdomain, client_id, session)
        return TokensResponse(access_token=tokens[0], refresh_token=tokens[1])

    except UserNotFoundException:
        logger.error(f"User with client_id: {client_id} and subdomain: {subdomain} not found")
        raise HTTPException(status_code=404, detail="User not found")

    except Exception as e:
        logger.exception(f"Error during token retrieval for client_id: {client_id}, subdomain: {subdomain}. Error: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving tokens")


async def start_get_tokens_consumer():
    connection_url = (
        f"amqp://{RMQ_USER}:{RMQ_PASSWORD}@{RMQ_HOST}:{RMQ_PORT}/{RMQ_VHOST}"
    )
    logger.info(f"Connecting to RabbitMQ at {connection_url}")

    await start_consumer(
        "tokens_get_user", connection_url, process_get_tokens_message
    )

    logger.info("Consumer for 'token_get_user' started.")
