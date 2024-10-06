# from typing import Dict
#
# from aiohttp import ClientSession
# from fastapi import Depends
# from sqlalchemy.ext.asyncio import AsyncSession
#
# from src.config import RMQ_USER, RMQ_PASSWORD, RMQ_HOST, RMQ_PORT, RMQ_VHOST
# from src.database import get_async_session
# from src.rabbitmq.consumer import start_consumer
# from loguru import logger
#
#
# async def process_tokens_users_config(data: dict, session: AsyncSession = Depends(get_async_session)):
#     try:
#         await process_config_widget(widget_data, session, client_session)
#         logger.info("Widget configuration processed successfully.")
#     except Exception as e:
#         logger.info("Error processing widget configuration", e)
#
#
# async def start_all_tokens_users_consumers():
#     connection_url = (
#         f"amqp://{RMQ_USER}:{RMQ_PASSWORD}@{RMQ_HOST}:{RMQ_PORT}/{RMQ_VHOST}"
#     )
#
#     # Запуск консюмера для каждой очереди
#     await start_consumer(
#         "leads_allocate_update_users", connection_url, process_tokens_users_config
#     )
#     await start_consumer(
#         "leads_allocate_get_users", connection_url, process_get_manager
#     )
