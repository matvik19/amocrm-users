from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.users.models import Users
from src.users.schemas import UserCreate, UserResponse, TokensResponse
from src.users.services import create_user, get_tokens_from_db, get_client_secret_redirect_url
from src.users.tokens_init import initialize_token_manager, get_new_tokens

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/add_user", response_model=UserResponse)
async def add_user(user: UserCreate, session: AsyncSession = Depends(get_async_session)):
    """Добавление пользователя в БД, сохранение его access_token и refresh_token"""

    try:
        client_secret, redirect_url = await get_client_secret_redirect_url(user.client_id, session)
        print(client_secret)

        access_token, refresh_token = await initialize_token_manager(
            user.client_id, client_secret, user.subdomain, user.code, redirect_url
        )

        new_user = await create_user(user.client_id, user.subdomain,
                                     access_token, refresh_token, session)

        return new_user

    except ValueError as ve:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "Error",
                "message": str(ve),
                "data": None
            }
        )

    except SQLAlchemyError:
        await session.rollback()
        raise HTTPException(
            status_code=500,
            detail={
                "status": "Error",
                "message": str(SQLAlchemyError),
                "data": None
            },
        )


@router.get("/get_user_tokens", response_model=TokensResponse)
async def get_tokens(subdomain: str, client_id: str, session: AsyncSession = Depends(get_async_session)):
    """Запрос на получение токенов пользователя из базы данных"""

    try:
        tokens = await get_tokens_from_db(subdomain, client_id, session)

        return tokens

    except ValueError as ve:
        raise HTTPException(
            status_code=404,
            detail={
                "status": "Error",
                "message": str(ve),
                "data": None
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "Error",
                "message": str(e),
                "data": None
            })
