from http import HTTPStatus
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

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
        raise HTTPException(HTTPStatus.CONFLICT, "User already exists with this email.")

    hashed_password_bytes = AuthenticationHandler.hash_password(user_dto.password)
    user_service.create_user(
        user_dto.email,
        user_dto.full_name,
        hashed_password_bytes
    )

    return AuthenticationHandler.sign_jwt(user.email)


@router.post("/login")
def login(user_dto: UserLoginDto, db: Session = Depends(get_db)):
    # TODO: check if user exist in DB
    # user = UserService.get_user_by_email(user.email)
    user_service = UserService(db)
    user = user_service.get_user_by_email(user_dto.email)

    if not user:
        raise HTTPException(
            HTTPStatus.BAD_REQUEST,
            detail="Email or password is invalid."
        )

    return AuthenticationHandler.sign_jwt(user.email)
