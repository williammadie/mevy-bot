from pydantic import BaseModel, EmailStr


class UserDto(BaseModel):
    full_name: str
    email: EmailStr
    password: str


class UserLoginDto(BaseModel):
    email: EmailStr
    password: str
