from http import HTTPStatus

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from mevy_bot.etl.gdrive_etl import GdriveEtl
from mevy_bot.etl.legifrance_etl import LegifranceEtl
from mevy_bot.services.workflow_service import WorkflowService
from mevy_bot.exceptions.workflows import JobActiveError, JobNotActiveError

router = APIRouter(prefix="/etl-workflows", tags=["ETL Workflows"])


class RunEtlWorkflowDto(BaseModel):
    predict_only: bool = Field(default=False)


@router.post("/{workflow_id}")
async def start_workflow(workflow_id: int):
    try:
        WorkflowService.start_workflow(workflow_id)
    except JobActiveError as exc:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Workflow is already active."
        ) from exc


@router.delete("/{workflow_id}")
async def stop_workflow(workflow_id: int):
    try:
        WorkflowService.stop_workflow(workflow_id)
    except JobNotActiveError as exc:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Workflow is currently inactive."
        ) from exc


@router.get("/active")
async def list_active_workflows():
    return {"active": WorkflowService.list_active_workflows()}


@router.get("/all")
async def list_workflows():
    return [
        {
            "id": 1,
            "name": "Google Drive",
            "description": "Watch files in Google Drive storage and update/delete/insert knowledge accordingly.",
            "isActive": False,
        },
        {
            "id": 2,
            "name": "Legifrance",
            "description": "Collect latest French laws and regulations.",
            "isActive": False,
        },
    ]
