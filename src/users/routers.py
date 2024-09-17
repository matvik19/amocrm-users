import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.users.exceptions import UserAlreadyExistsException, UserNotFoundException, WidgetNotFoundException
from src.users.models import Users
from src.users.schemas import UserCreate, UserResponse, TokensResponse
from src.users.services import create_user, get_tokens_from_db, get_client_secret_redirect_url, check_user_exists
from src.users.tokens_init import initialize_token_manager
from loguru import logger

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/add_user", response_model=UserResponse)
async def add_user(user: UserCreate, session: AsyncSession = Depends(get_async_session)) -> UserResponse:
    """Добавление пользователя в БД, сохранение его access_token и refresh_token"""

    try:
        await check_user_exists(user.client_id, user.subdomain, session)

        client_secret, redirect_url = await get_client_secret_redirect_url(user.client_id, session)
        access_token, refresh_token = await initialize_token_manager(
            user.client_id, client_secret, user.subdomain, user.code, redirect_url
        )

        new_user = await create_user(user.client_id, user.subdomain,
                                     access_token, refresh_token, session)

        return UserResponse(id=new_user.id, client_id=new_user.client_id, subdomain=new_user.subdomain)

    except UserAlreadyExistsException:
        logger.error("User with this client_id and subdomain already exists")
        raise
    except WidgetNotFoundException:
        logger.error("Widget with this client_id don't exists")
        raise
    except Exception as e:
        logger.exception(
            f"Value error during user creation. Client_id: {user.client_id}, Subdomain: {user.subdomain}, Error: {e}")
        raise HTTPException(status_code=500, detail="User creation error")


@router.get("/get_user_tokens", response_model=TokensResponse)
async def get_tokens(client_id: str, subdomain: str,
                     session: AsyncSession = Depends(get_async_session)) -> TokensResponse:
    """Запрос на получение токенов пользователя из базы данных"""

    try:
        tokens = await get_tokens_from_db(subdomain, client_id, session)
        return TokensResponse(access_token=tokens[0], refresh_token=tokens[1])

    except UserNotFoundException:
        logger.error("User with client_id and subdomain not found")
        raise
    except Exception as e:
        logger.exception(
            f"Value error during get tokens. User: {client_id}, Subdomain: {subdomain}, Error: {e}")
        raise HTTPException(status_code=500, detail="Error getting user token")


