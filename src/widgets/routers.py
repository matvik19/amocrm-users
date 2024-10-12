from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.widgets.models import Widgets
from src.widgets.schemas import WidgetResponse, WidgetCreate

router = APIRouter(prefix="/widgets", tags=["Widgets"])


@router.post("/create_acw", response_model=WidgetResponse)
async def add_widget(widget: WidgetCreate, session: AsyncSession = Depends(get_async_session)) -> WidgetResponse:
    """Добавление нового виджета в базу данных"""
    existing_widget = await session.execute(
        select(Widgets).where(
            Widgets.client_id == widget.client_id,
            Widgets.redirect_url == widget.redirect_url
        )
    )
    existing_widget = existing_widget.scalars().first()

    if existing_widget:
        raise HTTPException(
            status_code=400,
            detail="A widget with the same client_id and redirect_url already exists."
        )

    # Если виджет не найден, создаем новый
    new_widget = Widgets(
        client_id=widget.client_id,
        client_secret=widget.client_secret,
        redirect_url=widget.redirect_url
    )

    session.add(new_widget)
    await session.commit()
    await session.refresh(new_widget)

    return WidgetResponse(
        id=new_widget.id,
        client_id=new_widget.client_id,
        client_secret=new_widget.client_secret,
        redirect_url=new_widget.redirect_url
    )


# Роут для получения всех записей
@router.get("/get_all_acw", response_model=List[WidgetResponse])
async def get_widgets(session: AsyncSession = Depends(get_async_session)) -> List[WidgetResponse]:
    """Получение всех виджетов из базы данных"""
    result = await session.execute(select(Widgets))
    widgets = result.scalars().all()

    return [
        WidgetResponse(
            id=widget.id,
            client_id=widget.client_id,
            client_secret=widget.client_secret,
            redirect_url=widget.redirect_url
        )
        for widget in widgets
    ]


# Роут для получения одного виджета по client_id
@router.get("/get_acw", response_model=WidgetResponse)
async def get_widget(client_id: str, session: AsyncSession = Depends(get_async_session)) -> WidgetResponse:
    """Получение виджета по client_id"""
    result = await session.execute(select(Widgets).where(Widgets.client_id == client_id))
    widget = result.scalar_one_or_none()

    if not widget:
        raise HTTPException(status_code=404, detail="Widget not found")

    return WidgetResponse(
        id=widget.id,
        client_id=widget.client_id,
        client_secret=widget.client_secret,
        redirect_url=widget.redirect_url
    )


# Роут для удаления записи по client_id
@router.delete("/del_acw", response_model=dict)
async def delete_widget(client_id: str, session: AsyncSession = Depends(get_async_session)) -> dict:
    """Удаление виджета по client_id"""
    result = await session.execute(select(Widgets).where(Widgets.client_id == client_id))
    widget = result.scalar_one_or_none()

    if not widget:
        raise HTTPException(status_code=404, detail="Widget not found")

    await session.delete(widget)
    await session.commit()

    return {"status": "Widget deleted successfully"}