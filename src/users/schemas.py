from pydantic import BaseModel


class UserCreate(BaseModel):
    client_id: str
    code: str
    subdomain: str


class UserResponse(BaseModel):
    id: int
    client_id: str
    subdomain: str


class TokensResponse(BaseModel):
    access_token: str
    refresh_token: str
