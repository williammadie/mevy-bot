import os
import json
import tempfile
from typing import Self

from mevy_bot.path_finder import PathFinder
from mevy_bot.etl.workflow_etl import WorkflowEtl
from mevy_bot.services.legifrance_service import LegifranceService
from mevy_bot.vector_store.qdrant_collection import QdrantCollection
from mevy_bot.vector_store.vector_store import VectorStore
from mevy_bot.etl.workflow_logger import WorkflowLogger



class LegifranceEtl(WorkflowEtl):

    def __init__(self: Self, logger: WorkflowLogger) -> None:
        super().__init__(logger)
        self.legifrance_service = LegifranceService()

    async def run(self: Self, predict_only: bool = False) -> None:
        await super().run()
        self.logger.info("Step 1: Loading JSON referential...")
        sources_dict = self.load_json_referential()
        codes_to_load = sources_dict["codes"]
        self.logger.info("Step 1: JSON referential loaded.")

        self.logger.info("Step 2: Downloading codes from Legifrance API...")
        with tempfile.TemporaryDirectory() as tmp_dir:
            for code_name in codes_to_load:
                self.logger.info(f"Step 2: Downloading code {code_name} from Legifrance API...")
                self.legifrance_service.download_code(code_name, tmp_dir)
                self.logger.info("Step 2: Code {code_name} downloaded.")

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

            await vector_store.build_from_directory_files(
                self.collection_name, tmp_dir)

    def load_json_referential(self: Self) -> dict:
        data_storage_path = PathFinder.data_definition()
        filepath = os.path.join(data_storage_path, 'auto_sources.json')

        with open(filepath, mode='r', encoding='utf8') as f:
            raw_content = f.read()
            sources_dict = json.loads(raw_content)

        return sources_dict
