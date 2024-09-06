from typing import Tuple

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .exceptions import UserAlreadyExistsException, UserNotFoundException, WidgetNotFoundException
from .models import Users
from .schemas import UserCreate
from ..widgets.models import Widgets


async def create_user(client_id: str, subdomain: str,
                      access_token: str, refresh_token: str, session: AsyncSession) -> Users:
    """Создание пользователя в бд"""

    new_user = Users(
        client_id=client_id,
        subdomain=subdomain,
        access_token=access_token,
        refresh_token=refresh_token,
    )

    session.add(new_user)
    await session.commit()
    return new_user


async def get_tokens_from_db(subdomain: str, client_id: str, session: AsyncSession) -> Tuple[str, str]:
    """Запрос на получение токенов пользователя из базы данных"""

    query = select(Users.access_token, Users.refresh_token).filter_by(
        subdomain=subdomain,
        client_id=client_id
    )
    result = await session.execute(query)
    tokens_from_db = result.first()

    if tokens_from_db is None:
        raise UserNotFoundException()

    return tokens_from_db.access_token, tokens_from_db.refresh_token


async def get_client_secret_redirect_url(client_id: str, session: AsyncSession) -> Tuple[str, str]:
    """Запрос на получение client_secret, redirect_url из базы данных"""

    query = select(Widgets.client_secret, Widgets.redirect_url).filter_by(
        client_id=client_id
    )

    result = await session.execute(query)
    fields = result.first()

    if fields is None:
        raise WidgetNotFoundException()

    return fields.client_secret, fields.redirect_url


async def check_user_exists(client_id: str, subdomain: str, session: AsyncSession) -> None:
    """Запрос на существование пользователя"""

    query = select(Users).filter_by(client_id=client_id, subdomain=subdomain)
    result = await session.execute(query)
    user = result.scalars().first()

    if user:
        raise UserAlreadyExistsException()
