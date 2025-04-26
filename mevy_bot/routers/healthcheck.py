from fastapi import APIRouter

from mevy_bot.services.healthcheck_service import HealthcheckService

router = APIRouter(prefix="/healthcheck", tags=["Healthcheck"])

@router.get("/")
async def get_kpis():
    return HealthcheckService.get_kpis()