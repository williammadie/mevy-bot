from fastapi import APIRouter

from mevy_bot.vector_store.vector_store import VectorStore

router = APIRouter(prefix="/vector-store", tags=["Vector Store"])


@router.get("/healthcheck")
async def vector_store_healthcheck():
    result = VectorStore.healthcheck()
    return {"status": "UP" if result else "DOWN"}
