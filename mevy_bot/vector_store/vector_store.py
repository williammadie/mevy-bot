import logging
import os
from typing import Self, List

from qdrant_client.models import (
    ScoredPoint
)

from mevy_bot.exceptions.unsupported_file_type_error import UnsupportedFileTypeError
from mevy_bot.path_finder import PathFinder
from mevy_bot.file_reader import FileReader
from mevy_bot.text_chunker import TextChunker
from mevy_bot.vector_store.qdrant_collection import QdrantCollection
from mevy_bot.embedder.qdrant_embedding_converter import QdrantEmbeddingConverter
from mevy_bot.embedder.cost_predictor import CostPredictor
from mevy_bot.embedder.token_calculator import TokenCalculator
from mevy_bot.embedder.human_number import HumanNumber

l = logging.getLogger(__name__)


class VectorStore:

    def __init__(
        self: Self,
        store_client: QdrantCollection
    ) -> None:
        self.store_client: QdrantCollection = store_client
        self.embedder: QdrantEmbeddingConverter = QdrantEmbeddingConverter()
        self.ensure_directories_exist()

    def ensure_directories_exist(self) -> None:
        """ Create mandatory directories if missing """
        os.makedirs(PathFinder.data_storage(), exist_ok=True)

    def build_from_data_storage_files(self: Self, collection_name: str) -> None:
        """ Build a vector store from PDF files in data_storage dir """
        l.info("Building vector store from data storage files...")
        all_docs_text_chunks = []
        storage_dir = PathFinder.data_storage()
        for filename in os.listdir(storage_dir):
            if not filename.endswith('.pdf'):
                raise UnsupportedFileTypeError(filename)

            filepath = os.path.join(storage_dir, filename)
            file_reader = FileReader()
            file_text = file_reader.read_text_from_pdf(filepath)

            text_chunker = TextChunker()
            text_chunks = text_chunker.split_text_into_chunks(file_text)
            all_docs_text_chunks.extend(text_chunks)

            nb_tokens = 0
            for chunk in all_docs_text_chunks:
                nb_tokens += TokenCalculator.nb_tokens_in_text_chunk(chunk)
            l.info("Starting the embeddings generation for %s tokens (%s characters)",
                   HumanNumber.format(nb_tokens),
                   HumanNumber.format(len(all_docs_text_chunks)
                                      * TextChunker.CHUNK_SIZE)
                   )

            expected_cost = CostPredictor.calculate_cost_based_on_chunk_size(
                len(all_docs_text_chunks),
                TextChunker.CHUNK_SIZE
            )
            l.info("The embeddings generation for %s text chunks is expected to cost %f$",
                   HumanNumber.format(len(text_chunks)), expected_cost)
            print(len(text_chunks[0]))
            print(text_chunks[0])
            exit()
            vectors = self.embedder.get_embeddings_text_chunks(
                all_docs_text_chunks)
            self.store_client.insert_vectors_in_collection(
                vectors, collection_name)
        l.info("Vector store successfully built.")

    def search_in_store(
        self: Self,
        search_pattern: str,
        collection_name: str
    ) -> List[ScoredPoint]:
        """ Search a string pattern in vector store """
        text_chunker = TextChunker()
        text_chunks = text_chunker.split_in_chunks(search_pattern)
        if len(text_chunks) > 1:
            l.warning("Too many chunks (%d) in query. Only considering the first one.", len(
                text_chunks))

        # TODO: If the query is too long, only the first chunk will be considered
        response = self.embedder.embedding_model.generate_embeddings(
            text_chunks[0])
        point_embeddings = response.data[0].embedding

        return self.store_client.search_in_collection(
            collection_name,
            point_embeddings
        )
