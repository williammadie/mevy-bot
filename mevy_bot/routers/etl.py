import os
from http import HTTPStatus

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from mevy_bot.services.workflow_service import WorkflowService
from mevy_bot.exceptions.workflows import JobActiveError, JobNotActiveError
from mevy_bot.path_finder import PathFinder
from mevy_bot.file_reader import FileReader
from mevy_bot.authentication.cookie_authentication import CookieAuthentication

router = APIRouter(prefix="/etl-workflows", tags=["ETL Workflows"])


class RunEtlWorkflowDto(BaseModel):
    predict_only: bool = Field(default=False)


@router.post("/{workflow_id}", dependencies=[Depends(CookieAuthentication())])
async def start_workflow(workflow_id: int):
    try:
        WorkflowService.start_workflow(workflow_id)
    except JobActiveError as exc:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Workflow is already active."
        ) from exc


@router.delete("/{workflow_id}", dependencies=[Depends(CookieAuthentication())])
async def stop_workflow(workflow_id: int):
    try:
        WorkflowService.stop_workflow(workflow_id)
    except JobNotActiveError as exc:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Workflow is currently inactive."
        ) from exc


@router.get("/active", dependencies=[Depends(CookieAuthentication())])
async def list_active_workflows():
    return {"active": WorkflowService.list_active_workflows()}


@router.get("/all", dependencies=[Depends(CookieAuthentication())])
async def list_workflows():
    return WorkflowService.list_workflows()


@router.get("/logs/{workflow_id}", dependencies=[Depends(CookieAuthentication())])
async def retrieve_logs(workflow_id: int):
    workflow_log_file = os.path.join(
        PathFinder.workflow_log_dirpath(),
        f"{workflow_id}.log"
    )
    try:
        return FileReader.tail(workflow_log_file)
    except FileNotFoundError as exc:
        raise HTTPException(
            HTTPStatus.BAD_REQUEST,
            detail="No recorded logs for this workflow."
        ) from exc


@router.get("/details/{workflow_id}", dependencies=[Depends(CookieAuthentication())])
async def get_workflow_details(workflow_id: int):
    return WorkflowService.get_workflow_by_id(workflow_id)
