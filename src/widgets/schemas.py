from pydantic import BaseModel


class WidgetCreate(BaseModel):
    client_id: str
    client_secret: str
    redirect_url: str


class WidgetResponse(BaseModel):
    id: int
    client_id: str
    client_secret: str
    redirect_url: str
