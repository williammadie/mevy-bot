""" REST API Entrypoint """
import os

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from mevy_bot.routers import (
    etl,
    legifrance,
    vector_store,
    chat,
    auth,
    healthcheck
)

from mevy_bot.database.database_handler import DatabaseHandler

ORIGINS = os.environ.get("ALLOWED_ORIGINS")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """ Startup code """
    database_handler = DatabaseHandler()
    database_handler.ensure_database_exists()
    database_handler.create_all_tables()
    yield

app = FastAPI(title="Mevy Bot API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(etl.router)
app.include_router(vector_store.router)
app.include_router(legifrance.router)
app.include_router(chat.router)
app.include_router(auth.router)
app.include_router(healthcheck.router)
