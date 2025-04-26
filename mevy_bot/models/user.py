from pydantic import BaseModel, Field, EmailStr

class UserDto(BaseModel):
    full_name: str = Field()
    email: EmailStr = Field()
    password: str = Field()

class UserLoginDto(BaseModel):
    email: EmailStr = Field()
    password: str = Field()