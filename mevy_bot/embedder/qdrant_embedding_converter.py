import logging
import uuid
from abc import ABC
from typing import Self, List

from qdrant_client.http.models import PointStruct

from mevy_bot.embedder.openai_embedder import OpenAIEmbedder

l = logging.getLogger(__name__)

class QdrantEmbeddingConverter(ABC):

    def __init__(
        self: Self,
    ) -> None:
        self.embedding_model = OpenAIEmbedder()

    def get_embeddings_text_chunk(self: Self, text_chunk: str) -> PointStruct:
        response = self.embedding_model.generate_embeddings(text_chunk)

        point_embeddings = response.data[0].embedding
        point_id = str(uuid.uuid4())

        return PointStruct(
            id=point_id,
            vector=point_embeddings,
            payload={"text": text_chunk}
        )

    def get_embeddings_text_chunks(self: Self, text_chunks: List[str]) -> List[PointStruct]:
        nb_chunks = len(text_chunks)
        points = []
        for chunk_index, text_chunk in enumerate(text_chunks):
            point = self.get_embeddings_text_chunk(text_chunk)
            points.append(point)
            l.info("%d/%d chunks have been processed.", chunk_index + 1, nb_chunks)
        return points
