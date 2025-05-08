import logging
from http import HTTPStatus
from fastapi import APIRouter, HTTPException, Depends, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from mevy_bot.database.database_handler import DatabaseHandler
from mevy_bot.dtos.user import UserDto, UserLoginDto
from mevy_bot.authentication.authentication_handler import AuthenticationHandler
from mevy_bot.services.user_service import UserService
from mevy_bot.authentication.cookie_authentication import CookieAuthentication

router = APIRouter(prefix="/authentication", tags=["Authentication"])
db_handler = DatabaseHandler()

logger = logging.getLogger(__name__)


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
def login(user_dto: UserLoginDto, response: Response, db: Session = Depends(get_db)):
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

    response = JSONResponse(content={"message": "Login successful"})

    # Set the JWT token as an HTTP-only cookie
    response.set_cookie(
        key="access_token",  # Name of the cookie
        value=access_token,  # JWT token
        httponly=True,  # Prevent JavaScript access
        secure=True,  # Only send cookie over HTTPS
        max_age=access_token_ttl,  # Cookie expiration time
        samesite="none",     # Allows cross-origin requests
    )

    return response


@router.get("/me", dependencies=[Depends(CookieAuthentication())])
async def get_current_user_id(token: str = Depends(CookieAuthentication())):
    """ Return user ID if connected """
    payload = AuthenticationHandler.decode_jwt(token)
    if payload is None:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN,
                            detail="Invalid token payload")

    user_id = payload.get("user_id")
    logger.info("Payload: %s", user_id)
    return {"user_id": user_id}


@router.post("/logout")
async def logout(response: Response):
    """ Delete HTTP-Only session cookie """
    response.delete_cookie("access_token")
    return {"status": "success"}
