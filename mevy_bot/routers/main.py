""" REST API Entrypoint """


from fastapi import FastAPI

from mevy_bot.routers import (
    etl,
    legifrance,
    vector_store,
    chat
)

app = FastAPI(title="Mevy Bot API")

app.include_router(etl.router)
app.include_router(vector_store.router)
app.include_router(legifrance.router)
app.include_router(chat.router)
