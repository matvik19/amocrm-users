from pydantic import BaseModel


class UserCreate(BaseModel):
    client_id: str
    code: str
    subdomain: str


class UserResponse(BaseModel):
    client_id: str
    subdomain: str
    access_token: str
    refresh_token: str


class TokensResponse(BaseModel):
    access_token: str
    refresh_token: str


