from http import HTTPStatus
from fastapi import APIRouter, HTTPException

from mevy_bot.models.user import UserDto, UserLoginDto
from mevy_bot.authentication.authentication_handler import AuthenticationHandler

router = APIRouter(prefix="/authentication", tags=["Authentication"])

users = []

@router.post("/register")
async def register(user: UserDto):
    # TODO: insert user in DB (hash password first)
    users.append(user)
    return AuthenticationHandler.sign_jwt(user.email)


@router.post("/login")
async def login(user: UserLoginDto):
    # TODO: check if user exist in DB
    #user = UserService.get_user_by_email(user.email)
    if user not in users:
        raise HTTPException(
            HTTPStatus.BAD_REQUEST,
            detail="Email or password is invalid."
        )

    return AuthenticationHandler.sign_jwt(user.email)
