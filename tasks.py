from apscheduler.triggers.cron import CronTrigger
from fastapi import Depends
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
            print("Получаем пользователей из бд", users)

            for user in users:
                print("ID:", user.id)
                print("ТОКЕН РЕФРЕШ", user.refresh_token)
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

                print("Сам запрос stmt", stmt)

                await session.execute(stmt)

            await session.commit()
        print("Токены успешно обновлены")

    except Exception as e:
        raise ValueError(f"Ошибка записи новых токенов: {e}")


# def activate_background_task():
#     """Запуск фоновой задачи update_tokens"""
#
#     scheduler = AsyncIOScheduler()
#     trigger = CronTrigger(hour=16, minute=0)
#     scheduler.add_job(update_tokens, trigger)
#     scheduler.start()


def activate_background_task():
    """Запуск фоновой задачи update_tokens"""

    scheduler = AsyncIOScheduler()
    scheduler.add_job(update_tokens, CronTrigger(hour=21, minute=2))
    scheduler.start()