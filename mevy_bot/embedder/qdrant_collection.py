import os
from typing import Self, List, Sequence

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    ScoredPoint
)

VECTOR_DIMENSIONS = 1536
VECTOR_DISTANCE = Distance.COSINE


class QdrantCollection():

    def __init__(self: Self) -> None:
        self.url = os.getenv('QDRANT_DB_URL')
        self.client = QdrantClient(url=self.url)

    def create_collection(self: Self, name: str) -> None:
        self.client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(
                size=VECTOR_DIMENSIONS,
                distance=VECTOR_DISTANCE
            )
        )

    def insert_vectors_in_collection(
        self: Self,
        points: List[PointStruct],
        collection_name: str
    ) -> None:
        self.client.upsert(
            collection_name=collection_name,
            wait=True,
            points=points
        )

    def search_in_collection(
        self: Self,
        collection_name: str,
        embeddings: Sequence[float],
        max_output_documents: int = 3
    ) -> List[ScoredPoint]:
        return self.client.search(
            collection_name=collection_name,
            query_vector=embeddings,
            limit=max_output_documents
        )
