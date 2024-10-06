# import json
# from loguru import logger
#
# import aio_pika
# from src.database import get_async_session
#
#
# async def process_message(message: aio_pika.IncomingMessage, process_func):
#     """
#     :param message: Сообщение из очереди RabbitMQ.
#     :param process_func: Функция для обработки данных сообщения.
#     """
#     async with message.process():
#         body = message.body.decode("utf-8")
#         data = json.loads(body)
#         print(f"Message received: {data}")
#
#         session_gen = get_async_session()
#         session = await anext(session_gen)
#
#         try:
#             await process_func(data, session)
#         except Exception as e:
#             logger.info("Error processing message.", e)
#             print(f"Error processing message: {e}")
#         finally:
#             await session_gen.aclose()
#
#
# async def start_consumer(queue_name: str, connection_url: str, process_func):
#     """
#     :param queue_name: Название очереди RabbitMQ.
#     :param connection_url: URL подключения к RabbitMQ.
#     :param process_func: Функция для обработки сообщений.
#     """
#     connection = await aio_pika.connect_robust(connection_url)
#     channel = await connection.channel()
#
#     queue = await channel.declare_queue(queue_name, durable=True)
#
#     async with queue.iterator() as queue_iter:
#         async for message in queue_iter:
#             await process_message(message, process_func)
