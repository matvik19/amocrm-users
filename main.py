import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.log_config import setup_logging
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


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
