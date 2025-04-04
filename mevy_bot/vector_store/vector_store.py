import logging
import os
from typing import Self, List
from decimal import Decimal

from qdrant_client.models import (
    ScoredPoint
)

from mevy_bot.file_reader import FileReader
from mevy_bot.text_chunker import TextChunker
from mevy_bot.vector_store.qdrant_collection import QdrantCollection
from mevy_bot.embedder.qdrant_embedding_converter import QdrantEmbeddingConverter
from mevy_bot.embedder.openai_embedder import OpenAIEmbedder
from mevy_bot.embedder.cost_predictor import CostPredictor
from mevy_bot.embedder.token_calculator import TokenCalculator
from mevy_bot.embedder.human_number import HumanNumber
from mevy_bot.models.openai import EmbeddingModel, ChatModel

l = logging.getLogger(__name__)


class VectorStore:

    CHUNK_SIZE = 1024
    CHUNK_OVERLAP = 0.2

    def __init__(
        self: Self,
        store_client: QdrantCollection,
        embedding_model: EmbeddingModel,
        chat_model: ChatModel
    ) -> None:
        self.store_client: QdrantCollection = store_client
        self.embedder = OpenAIEmbedder(embedding_model)
        self.embedding_converter = QdrantEmbeddingConverter(self.embedder)
        self.embedding_model = embedding_model
        self.chat_model = chat_model

    def build_from_directory_files(
        self: Self,
        collection_name: str,
        target_dir: str
    ) -> None:
        """ Build a vector store from PDF files in target dir """
        l.info("Building vector store from data storage files...")
        for root, _, files in os.walk(target_dir):
            for filename in files:
                l.info("Processing %s...", filename)
                filepath = os.path.join(root, filename)

                text_chunker = TextChunker(
                    self.embedding_model, self.chat_model)
                text_chunks = text_chunker.chunks_from_document(
                    filepath,
                    self.CHUNK_SIZE,
                    self.CHUNK_OVERLAP
                )

                vectors = self.embedding_converter.get_embeddings_text_chunks(
                    text_chunks,
                    filename
                )
                self.store_client.insert_vectors_in_collection(
                    vectors, collection_name)
        l.info("Vector store successfully built.")

    def predict_costs_for_embedding_files(self: Self, target_dir: str) -> None:
        total_cost = Decimal("0")
        total_chars, total_tokens, total_chunks = 0, 0, 0
        for root, _, files in os.walk(target_dir):
            for filename in files:
                filepath = os.path.join(root, filename)
                file_reader = FileReader()
                file_text = file_reader.detect_format_and_read(filepath)

                token_calculator = TokenCalculator(self.chat_model)
                nb_tokens, nb_chars = token_calculator.nb_tokens_nb_chars(
                    file_text)
                total_tokens += nb_tokens
                total_chars += nb_chars
                l.info(
                    "Embeddings generation for %s tokens (%s characters) [%s]",
                    HumanNumber.format(nb_tokens),
                    HumanNumber.format(nb_chars),
                    filename
                )

                text_chunker = TextChunker(
                    self.embedding_model, self.chat_model)
                text_chunks = text_chunker.split_in_chunks_semchunk(
                    file_text, self.CHUNK_SIZE, self.CHUNK_OVERLAP)
                total_chunks += len(text_chunks)

                cost_predictor = CostPredictor(
                    self.embedding_model.price_per_1k_input_tokens)
                expected_cost = cost_predictor.calculate_cost_based_on_token_count(
                    Decimal(nb_tokens))
                total_cost += expected_cost
                l.info("Embeddings generation for %s text chunks is expected to cost %f$ [%s]",
                       HumanNumber.format(len(text_chunks)), expected_cost, filename)
            l.info(
                "\n[TOTAL] Embeddings generation for %s tokens (%s characters) [total]",
                HumanNumber.format(total_tokens),
                HumanNumber.format(total_chars)
            )
            l.info("[TOTAL] Embeddings generation for %s text chunks is expected to cost %f$ [total]",
                   HumanNumber.format(total_chunks), total_cost)

    def search_in_store(
        self: Self,
        search_pattern: str,
        collection_name: str
    ) -> List[ScoredPoint]:
        """ Search a string pattern in vector store """
        text_chunker = TextChunker(self.embedding_model, self.chat_model)
        text_chunks = text_chunker.split_in_chunks_semchunk(
            search_pattern, self.CHUNK_SIZE, self.CHUNK_OVERLAP)
        if len(text_chunks) > 1:
            l.warning("Too many chunks (%d) in query. Only considering the first one.", len(
                text_chunks))

        # TODO: If the query is too long, only the first chunk will be considered
        response = self.embedding_converter.embedder.generate_embeddings(
            text_chunks[0])
        point_embeddings = response.data[0].embedding

        return self.store_client.search_in_collection(
            collection_name,
            point_embeddings
        )

    def delete_vectors_for_source(self: Self, collection_name: str, source_name: str) -> None:
        l.info(
            "Deleting points in vector store for %s...", source_name)
        self.store_client.delete_vectors_for_source(
            collection_name, source_name)
        l.info("Points deleted.")

    @staticmethod
    def delete_collection(collection_name: str) -> None:
        return QdrantCollection.delete_collection(collection_name)

    @staticmethod
    def healthcheck() -> bool:
        return QdrantCollection.healthcheck()
