from fastapi import APIRouter
from pydantic import BaseModel, Field

from mevy_bot.etl.gdrive_etl import GdriveEtl
from mevy_bot.etl.legifrance_etl import LegifranceEtl

router = APIRouter(prefix="/etl-workflows", tags=["ETL Workflows"])


class RunEtlWorkflowDto(BaseModel):
    predict_only: bool = Field(default=False)


@router.post("/gdrive")
async def run_gdrive_etl_workflow(dto: RunEtlWorkflowDto):
    gdrive_etl = GdriveEtl()
    gdrive_etl.run(predict_only=dto.predict_only)

    return {"message": "Google Drive ETL workflow completed with success!"}


@router.post("/legifrance")
async def run_legifrance_etl_workflow(dto: RunEtlWorkflowDto):
    legifrance_etl = LegifranceEtl()
    legifrance_etl.run(predict_only=dto.predict_only)

    return {"message": "Google Drive ETL workflow completed with success!"}
