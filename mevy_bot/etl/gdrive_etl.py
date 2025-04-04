import logging
import tempfile
import itertools
from typing import Self

from mevy_bot.etl.workflow_etl import WorkflowEtl
from mevy_bot.services.gdrive_service import GdriveService
from mevy_bot.services.gdrive_cache_service import GdriveCacheService
from mevy_bot.vector_store.vector_store import VectorStore
from mevy_bot.vector_store.qdrant_collection import QdrantCollection

logger = logging.getLogger()


class GdriveEtl(WorkflowEtl):

    def __init__(self: Self) -> None:
        super().__init__()
        self.gdrive_service = GdriveService()
        self.gdrive_cache_service = GdriveCacheService()
        self.store_client = QdrantCollection(
            self.embedding_model_info.vector_dimensions)
        self.vector_store = VectorStore(
            self.store_client,
            self.embedding_model_info,
            self.generator_model_info
        )

    def run(self: Self, predict_only=False) -> None:
        super().run()
        logger.info("Step 1: Listing files in Google Drive folder...")
        knowledge_files = self.gdrive_service.list_knowledge_files()
        logger.info("Step 1: %d files in folder.", len(knowledge_files["files"]))

        logger.info("Step 2: Determining files to create, update and delete...")
        cached_files = self.gdrive_cache_service.read()

        files_to_create = []
        files_to_update = []
        for file_data in knowledge_files["files"]:
            if file_data['id'] not in cached_files:
                files_to_create.append(file_data)

            elif file_data["modifiedTime"] != cached_files[file_data["id"]]["modifiedTime"]:
                files_to_update.append(file_data)

        files_to_delete = []
        knowledge_file_ids = [file_data["id"] for file_data in knowledge_files["files"]]
        for file_id, file_data in cached_files.items():
            if file_id not in knowledge_file_ids:
                files_to_delete.append({"id": file_id, "name": file_data["name"]})
        logger.info(
            "Step 2: Results=(%d create, %d update, %d delete)",
            len(files_to_create),
            len(files_to_update),
            len(files_to_delete)
        )

        logger.info(
            "Step 3: Deleting deleted and updated files from vector store...")
        for file_data in itertools.chain(files_to_update, files_to_delete):
            self.vector_store.delete_vectors_for_source(
                self.collection_name, file_data["name"])
        logger.info(
            "Step 3: Deleted and updated files have been deleted from vector store.")

        logger.info("Step 4: Downloading files from Google Drive...")
        with tempfile.TemporaryDirectory() as tmp_dir:
            for file in itertools.chain(files_to_create, files_to_update):
                logger.info("Step 4: Downloading file %s...", file)
                self.gdrive_service.download_and_write_file(
                    file["id"], file["name"], tmp_dir)
                logger.info("Step 4: File %s downloaded.", file)
                logger.info("Step 4: All files have been downloaded.")

                if predict_only:
                    self.vector_store.predict_costs_for_embedding_files(
                        tmp_dir)
                    return

                self.vector_store.build_from_directory_files(
                    self.collection_name, tmp_dir)
        logger.info("Step 5: Updating known files cache...")
        self._update_cache(files_to_create, files_to_update,
                           files_to_delete, cached_files)
        logger.info("Step 5: Cache updated.")

        logger.info("Workflow complete.")

    def _update_cache(
        self: Self,
        files_to_create: list,
        files_to_update: list,
        files_to_delete: list,
        cached_files: dict,
    ) -> None:
        for file_data in files_to_delete:
            logger.info("Deleting file %s (id %s) from cache...",
                        file_data["name"], file_data["id"])
            cached_files.pop(file_data["id"])
            logger.info("File info deleted from cache.")

        for file_data in files_to_update:
            logger.info("Updating file info %s (id %s) in cache...",
                        file_data["name"], file_data["id"])
            cached_files[file_data["id"]]["modifiedTime"] = file_data["modifiedTime"]
            logger.info("File info updated in cache.")

        for file_data in files_to_create:
            logger.info("Adding file %s (id %s) to cache...",
                        file_data["name"], file_data["id"])
            cached_files[file_data["id"]] = {
                "name": file_data["name"],
                "modifiedTime": file_data["modifiedTime"]
            }
            logger.info("File created in cache.")

        self.gdrive_cache_service.write(cached_files)
