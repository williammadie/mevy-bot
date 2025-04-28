from datetime import datetime, timedelta

from http import HTTPStatus
from fastapi import APIRouter, HTTPException, Depends, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import pytz

from mevy_bot.database.database_handler import DatabaseHandler
from mevy_bot.dtos.user import UserDto, UserLoginDto
from mevy_bot.authentication.authentication_handler import AuthenticationHandler
from mevy_bot.services.user_service import UserService

router = APIRouter(prefix="/authentication", tags=["Authentication"])
db_handler = DatabaseHandler()


def get_db():
    db = db_handler.get_session()
    try:
        yield db
    finally:
        db.close()


@router.post("/register")
def register(user_dto: UserDto, db: Session = Depends(get_db)):
    # TODO: insert user in DB (hash password first)
    user_service = UserService(db)
    user = user_service.get_user_by_email(user_dto.email)

    if user:
        raise HTTPException(HTTPStatus.CONFLICT,
                            "User already exists with this email.")

    hashed_password_bytes = AuthenticationHandler.hash_password(
        user_dto.password)
    user_service.create_user(
        user_dto.email,
        user_dto.full_name,
        hashed_password_bytes
    )

    return AuthenticationHandler.sign_jwt(user_dto.email)


@router.post("/login")
def login(user_dto: UserLoginDto, db: Session = Depends(get_db), response: Response = None):
    user_service = UserService(db)
    user = user_service.get_user_by_email(user_dto.email)

    if not user:
        raise HTTPException(
            HTTPStatus.FORBIDDEN,
            detail="Email or password is invalid."
        )

    is_pwd_correct = AuthenticationHandler.is_password_correct(
        user_dto.password,
        user.password_hash
    )
    if not is_pwd_correct:
        raise HTTPException(
            HTTPStatus.FORBIDDEN,
            detail="Email or password is invalid."
        )

    # Create the JWT token using AuthenticationHandler
    access_token = AuthenticationHandler.sign_jwt(user_dto.email)
    access_token_ttl = AuthenticationHandler.JWT_TTL_IN_SECONDS

    # Set the JWT token as an HTTP-only cookie
    response.set_cookie(
        key="access_token",  # Name of the cookie
        value=access_token,  # JWT token
        httponly=True,  # Prevent JavaScript access
        secure=True,  # Only send cookie over HTTPS
        max_age=access_token_ttl,  # Cookie expiration time
        samesite="strict"  # Prevent the cookie from being sent in cross-site requests
    )

    return JSONResponse(content={"message": "Login successful"})
