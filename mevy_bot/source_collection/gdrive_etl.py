import os
import logging
import tempfile
from typing import Self

from mevy_bot.source_collection.workflow_etl import WorkflowEtl
from mevy_bot.services.gdrive_service import GdriveService

logger = logging.getLogger()


class GdriveEtl(WorkflowEtl):

    def __init__(self: Self) -> None:
        self.gdrive_service = GdriveService()

    def run(self: Self, predict_only=False) -> None:
        super().run()
        logger.info("Step 1: Listing files in Google Drive folder...")
        knowledge_files = self.gdrive_service.list_knowledge_files()
        logger.info("Step 1: %d files in folder.", len(knowledge_files))

        logger.info("Step 2: Downloading files from Google Drive...")
        with tempfile.TemporaryDirectory() as tmp_dir:
            for file in knowledge_files["files"]:
                logger.info("Step 2: Downloading file %s...", file)
                self.gdrive_service.download_and_write_file(
                    file["id"], file["name"], tmp_dir)
                logger.info("Step 2: File %s downloaded.", file)
        logger.info("Step 2: All files have been downloaded.")

if __name__ == "__main__":
    gdrive_etl = GdriveEtl()
    gdrive_etl.run()