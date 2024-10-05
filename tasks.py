from apscheduler.triggers.cron import CronTrigger
from fastapi import Depends
from loguru import logger
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from src.users.services import get_client_secret_redirect_url
from src.users.tokens_init import get_new_tokens
from src.database import get_async_session, async_session_maker
from src.users.models import Users


async def update_tokens():
    """Обновление access_token, refresh_token по старому refresh_tonken пользователя"""

    try:
        async with async_session_maker() as session:
            result = await session.execute(select(Users))
            users = result.scalars().all()

            for user in users:
                client_secret = await get_client_secret_redirect_url(user.client_id, session)
                new_access_token, new_refresh_token = await get_new_tokens(
                    user.subdomain, user.refresh_token, user.client_id, client_secret[0]
                )
                print("НОВЫЙ АКССЕСС: ", new_access_token)
                print("НОВЫЙ РЕФРЕШ: ", new_refresh_token)

                stmt = (
                    update(Users)
                    .filter_by(id=user.id)
                    .values(access_token=new_access_token, refresh_token=new_refresh_token)
                )

                await session.execute(stmt)

            await session.commit()
        logger.info("Токены успешно обновлены")

    except Exception as e:
        logger.error(f"Ошибка записи новых токенов: {e}")


def activate_background_task():
    """Запуск фоновой задачи update_tokens"""

    scheduler = AsyncIOScheduler()
    scheduler.add_job(update_tokens, CronTrigger(hour=13, minute=15, timezone="UTC"))
    scheduler.start()

    logger.info("Фоновая задача по обновлению токенов запущена")
