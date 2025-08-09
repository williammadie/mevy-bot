""" REST API Entrypoint """
import os
import sys
import logging

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from mevy_bot.routers import (
    etl,
    legifrance,
    vector_store,
    chat,
    auth,
    healthcheck,
    document
)

from mevy_bot.database.database_handler import DatabaseHandler
from mevy_bot.services.user_service import UserService
from mevy_bot.authentication.authentication_handler import AuthenticationHandler

logger = logging.getLogger(__name__)

ORIGINS = os.environ.get("ALLOWED_ORIGINS")


def create_first_user(db_session: Session):
    # Ensure user attributes are set
    user_email = os.environ.get("FIRST_USER_EMAIL")
    user_name = os.environ.get("FIRST_USER_NAME")
    user_password = os.environ.get("FIRST_USER_PASSWORD")
    if any(var is None for var in [user_email, user_name, user_password]):
        sys.exit(
            "Environment variables for FIRST_USER_EMAIL, FIRST_USER_NAME, and FIRST_USER_PASSWORD must be set."
        )

    # Check if the user already exists
    user_service = UserService(db_session)
    user = user_service.get_user_by_email(user_email)
    if user:
        logger.info("User %s already exists, skipping creation.", user_email)
        return

    # Create the first user
    logger.info("Creating first user with email: %s", user_email)
    hashed_password_bytes = AuthenticationHandler.hash_password(user_password)
    user_service.create_user(
        user_email,
        user_name,
        hashed_password_bytes
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """ Startup code """
    database_handler = DatabaseHandler()
    database_handler.ensure_database_exists()
    database_handler.create_all_tables()

    db_session = database_handler.get_session()
    try:
        create_first_user(db_session)
    finally:
        db_session.close()
    yield

APP_MODE = os.environ.get("APP_MODE", "production").lower()

if APP_MODE == "production":
    logger.info("Disabling API documentation in production mode")
    DOCS_URL = None
    REDOC_URL = None
    OPEN_API_URL = None
else:
    logger.info("Enabling API documentation in development mode")
    DOCS_URL = "/docs"
    REDOC_URL = "/redoc"
    OPEN_API_URL = "/openapi.json"

app = FastAPI(
    title="Mevy Bot API",
    lifespan=lifespan,
    docs_url=DOCS_URL,
    redoc_url=REDOC_URL,
    openapi_url=OPEN_API_URL
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers['Strict-Transport-Security'] = 'max-age=63072000; includeSubDomains'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    # response.headers['Content-Security-Policy'] = "default-src 'self'"
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

app.include_router(etl.router)
app.include_router(vector_store.router)
app.include_router(legifrance.router)
app.include_router(chat.router)
app.include_router(auth.router)
app.include_router(healthcheck.router)
app.include_router(document.router)
