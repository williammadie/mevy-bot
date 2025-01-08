import uuid
from abc import ABC
from typing import Self, List

from qdrant_client.http.models import PointStruct

from mevy_bot.embedder.openai_embedder import OpenAIEmbedder


class QdrantEmbeddingConverter(ABC):

    def __init__(
        self: Self
    ) -> None:
        self.embedder = OpenAIEmbedder()

    def get_embeddings_text_chunk(self: Self, text_chunk: str) -> PointStruct:
        response = self.embedder.generate_embeddings(text_chunk)

        point_embeddings = response['data'][0]['embedding']
        point_id = str(uuid.uuid4())

        return PointStruct(
            id=point_id,
            vector=point_embeddings,
            payload={"text": text_chunk}
        )

    def get_embeddings_text_chunks(self: Self, text_chunks: List[str]) -> List[PointStruct]:
        points = []
        for text_chunk in text_chunks:
            point = self.get_embeddings_text_chunk(text_chunk)
            points.append(point)
        return points
