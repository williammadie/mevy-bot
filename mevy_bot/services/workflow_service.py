import asyncio
import logging

from mevy_bot.models.workflows import WorkflowInfo
from mevy_bot.exceptions.workflows import JobActiveError, JobNotActiveError

l = logging.getLogger()


class WorkflowService:
    active_workflows: dict[int, WorkflowInfo] = {}

    @staticmethod
    def start_workflow(workflow_id: int) -> None:
        if workflow_id in WorkflowService.active_workflows:
            raise JobActiveError()

        # Create a dedicated task
        launched_task = asyncio.create_task(
            WorkflowService.workflow_loop(workflow_id)
        )

        # Update workflows registry
        workflow_info = WorkflowInfo(launched_task)
        WorkflowService.active_workflows[workflow_id] = workflow_info

    @staticmethod
    async def workflow_loop(workflow_id: int) -> None:
        try:
            while True:
                l.info("Hello world!")
                await asyncio.sleep(60)
        except asyncio.CancelledError:
            l.info("Workflow %d has been stopped.", workflow_id)

    @staticmethod
    def stop_workflow(workflow_id: int) -> None:
        if workflow_id not in WorkflowService.active_workflows:
            raise JobNotActiveError()

        # Retrieve and cancel asyncio task associated to workflow
        workflow = WorkflowService.active_workflows[workflow_id]
        workflow.asyncio_task.cancel()

        # Update workflows registry
        WorkflowService.active_workflows.pop(workflow_id)

    @staticmethod
    def list_active_workflows() -> list:
        return list(WorkflowService.active_workflows.keys())
