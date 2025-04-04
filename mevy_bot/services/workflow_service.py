import logging
import time
import multiprocessing

from mevy_bot.models.workflows import WorkflowInfo
from mevy_bot.exceptions.workflows import JobActiveError, JobNotActiveError
from mevy_bot.factories.workflow_factory import WorkflowFactory
from mevy_bot.etl.workflow_etl import WorkflowEtl

l = logging.getLogger()


class WorkflowService:
    active_workflows: dict[int, WorkflowInfo] = {}

    @staticmethod
    def start_workflow(workflow_id: int) -> None:
        if workflow_id in WorkflowService.active_workflows:
            raise JobActiveError()

        # Create a dedicated process
        l.info("Creating a process for workflow %d...", workflow_id)
        workflow_process = multiprocessing.Process(
            target=WorkflowService.workflow_loop,
            args=(workflow_id,),
            daemon=True  # Process shuts down if main process shuts down
        )
        workflow_process.start()
        l.info("Process for workflow %d created.", workflow_id)

        # Update workflows registry
        workflow_info = WorkflowInfo(workflow_process)
        WorkflowService.active_workflows[workflow_id] = workflow_info

    @staticmethod
    def workflow_loop(workflow_id: int) -> None:
        workflow: WorkflowEtl = WorkflowFactory.create_workflow(
            workflow_id)
        while True:
            workflow.run()
            time.sleep(60)

    @staticmethod
    def stop_workflow(workflow_id: int) -> None:
        if workflow_id not in WorkflowService.active_workflows:
            raise JobNotActiveError()

        # Retrieve and stop process associated to workflow
        workflow = WorkflowService.active_workflows[workflow_id]
        l.info("Waiting for process to stop (Workflow %d).", workflow_id)
        workflow.workflow_process.terminate()
        l.info("Workflow %d process has been stopped.", workflow_id)

        # Update workflows registry
        WorkflowService.active_workflows.pop(workflow_id)

    @staticmethod
    def list_active_workflows() -> list:
        return list(WorkflowService.active_workflows.keys())

if __name__  == "__main__":
    workflow_service = WorkflowService()
    workflow_service.workflow_loop(1)