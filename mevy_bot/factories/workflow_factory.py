import logging

from mevy_bot.etl.workflow_etl import WorkflowEtl
from mevy_bot.etl.gdrive_etl import GdriveEtl
from mevy_bot.etl.legifrance_etl import LegifranceEtl
from mevy_bot.etl.workflow_logger import WorkflowLogger

l = logging.getLogger()


class WorkflowFactory():

    @staticmethod
    def create_workflow(workflow_id: int) -> WorkflowEtl:
        workflow_logger = WorkflowLogger(workflow_id)
        if workflow_id == 1:
            l.info("Instanciating Google Drive Workflow...")
            return GdriveEtl(workflow_logger)
        elif workflow_id == 2:
            l.info("Instanciating Legifrance Workflow...")
            return LegifranceEtl(workflow_logger)
        else:
            raise ValueError(f"Workflow with id {workflow_id} does not exist.")
