import logging

from mevy_bot.etl.workflow_etl import WorkflowEtl
from mevy_bot.etl.gdrive_etl import GdriveEtl
from mevy_bot.etl.legifrance_etl import LegifranceEtl

l = logging.getLogger()

class WorkflowFactory():

    @staticmethod
    def create_workflow(workflow_id: int) -> WorkflowEtl:
        if workflow_id == 1:
            l.info("Instanciating Google Drive Workflow...")
            return GdriveEtl()
        elif workflow_id == 2:
            l.info("Instanciating Legifrance Workflow...")
            return LegifranceEtl()
        else:
            raise ValueError(f"Workflow with id {workflow_id} does not exist.")
        