import os
import json
import logging
import tempfile
from typing import Self

from mevy_bot.path_finder import PathFinder
from mevy_bot.source_collection.workflow_etl import WorkflowEtl
from mevy_bot.legifrance.law_text_downloader import LawTextDownloader
from mevy_bot.models.openai import OpenAIModelFactory
from mevy_bot.vector_store.qdrant_collection import QdrantCollection
from mevy_bot.vector_store.vector_store import VectorStore

logger = logging.getLogger()


class LegifranceEtl(WorkflowEtl):

    def __init__(self: Self) -> None:
        self.law_text_downloader = LawTextDownloader()
        self.embedding_model_info = OpenAIModelFactory.text_embedding_3_small()
        self.generator_model_info = OpenAIModelFactory.gpt4o_mini()
        self.collection_name = "mevy_bot"

    def run(self: Self, predict_only: bool = False) -> None:
        super().run()
        logger.info("Step 1: Loading JSON referential...")
        sources_dict = self.load_json_referential()
        codes_to_load = sources_dict["codes"]
        logger.info("Step 1: JSON referential loaded.")

        logger.info("Step 2: Downloading codes from Legifrance API...")
        with tempfile.TemporaryDirectory() as tmp_dir:
            for code_name in codes_to_load:
                logger.info("Step 2: Downloading code %s from Legifrance API...",
                            code_name)
                self.law_text_downloader.download_code(code_name, tmp_dir)
                logger.info("Step 2: Code %s downloaded.", code_name)

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

    def load_json_referential(self: Self) -> dict:
        data_storage_path = PathFinder.data_definition()
        filepath = os.path.join(data_storage_path, 'auto_sources.json')

        with open(filepath, mode='r', encoding='utf8') as f:
            raw_content = f.read()
            sources_dict = json.loads(raw_content)

        return sources_dict
