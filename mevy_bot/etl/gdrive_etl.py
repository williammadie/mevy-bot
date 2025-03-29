import os
import logging
import tempfile
from typing import Self

from mevy_bot.etl.workflow_etl import WorkflowEtl
from mevy_bot.services.gdrive_service import GdriveService
from mevy_bot.vector_store.vector_store import VectorStore
from mevy_bot.vector_store.qdrant_collection import QdrantCollection

logger = logging.getLogger()


class GdriveEtl(WorkflowEtl):

    def __init__(self: Self) -> None:
        super().__init__()
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

                store_client = QdrantCollection(
                    self.embedding_model_info.vector_dimensions)
                vector_store = VectorStore(
                    store_client,
                    self.embedding_model_info,
                    self.generator_model_info
                )

                if predict_only:
                    vector_store.predict_costs_for_embedding_files(tmp_dir)
                    return

                vector_store.build_from_directory_files(
                    self.collection_name, tmp_dir)


if __name__ == "__main__":
    gdrive_etl = GdriveEtl()
    gdrive_etl.run()
