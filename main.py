import asyncio

import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.log_config import setup_logging
from src.rabbitmq.consumer_create_users import start_token_add_user_consumer
from src.rabbitmq.consumer_get_user import start_get_tokens_consumer
from src.users.routers import router as router_users
from src.widgets.routers import router as router_widgets

from tasks import activate_background_task
from loguru import logger

app = FastAPI(title="Allocation widget")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router_users)
app.include_router(router_widgets)


@app.on_event("startup")
async def startup_event():
    setup_logging()
    logger.info("Service users has been started")
    activate_background_task()

    loop = asyncio.get_event_loop()
    loop.create_task(start_token_add_user_consumer())
    loop.create_task(start_get_tokens_consumer())


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
