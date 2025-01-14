import logging
import os
from typing import Self, List
from decimal import Decimal


from qdrant_client.models import (
    ScoredPoint
)

from mevy_bot.exceptions.unsupported_file_type_error import UnsupportedFileTypeError
from mevy_bot.path_finder import PathFinder
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
        self.ensure_directories_exist()

    def ensure_directories_exist(self) -> None:
        """ Create mandatory directories if missing """
        os.makedirs(PathFinder.data_storage(), exist_ok=True)

    def build_from_data_storage_files(self: Self, collection_name: str) -> None:
        """ Build a vector store from PDF files in data_storage dir """
        l.info("Building vector store from data storage files...")
        storage_dir = PathFinder.data_storage()
        l.info("%d files detected in storage.", len(os.listdir(storage_dir)))
        for filename in os.listdir(storage_dir):
            l.info("Processing %s...", filename)
            if not filename.endswith('.pdf'):
                raise UnsupportedFileTypeError(filename)

            filepath = os.path.join(storage_dir, filename)
            text_chunker = TextChunker(self.embedding_model, self.chat_model)
            text_chunks = text_chunker.chunks_from_document(
                filepath,
                self.CHUNK_SIZE,
                self.CHUNK_OVERLAP
            )

            vectors = self.embedding_converter.get_embeddings_text_chunks(
                text_chunks)
            self.store_client.insert_vectors_in_collection(
                vectors, collection_name)
        l.info("Vector store successfully built.")

    def predict_costs_of_store_building(self: Self) -> None:
        storage_dir = PathFinder.data_storage()
        total_cost = Decimal("0")
        total_chars, total_tokens, total_chunks = 0, 0, 0
        for filename in os.listdir(storage_dir):
            if not filename.endswith('.pdf'):
                raise UnsupportedFileTypeError(filename)

            filepath = os.path.join(storage_dir, filename)
            file_reader = FileReader()
            file_text = file_reader.read_text_from_pdf(filepath)

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

            text_chunker = TextChunker(self.embedding_model, self.chat_model)
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
            "Embeddings generation for %s tokens (%s characters) [total]",
            HumanNumber.format(total_tokens),
            HumanNumber.format(total_chars)
        )
        l.info("Embeddings generation for %s text chunks is expected to cost %f$ [total]",
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
