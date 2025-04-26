""" REST API Entrypoint """

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

ORIGINS = [
    "http://127.0.0.1:5173"
]

app = FastAPI(title="Mevy Bot API")

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
