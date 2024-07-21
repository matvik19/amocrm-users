from fastapi import HTTPException


class UserAlreadyExistsException(HTTPException):
    def __init__(self):
        super().__init__(status_code=409, detail="User with this client_id and subdomain already exists")


class UserNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="User not found")