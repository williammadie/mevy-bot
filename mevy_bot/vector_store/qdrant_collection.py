import os
from typing import Self, List, Sequence

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    ScoredPoint
)

VECTOR_DISTANCE = Distance.COSINE


class QdrantCollection():

    def __init__(self: Self, vector_dimensions: int) -> None:
        self.vectore_dimensions = vector_dimensions
        self.url = os.getenv('QDRANT_DB_URL')
        self.client = QdrantClient(url=self.url)

    def create_collection(self: Self, name: str) -> None:
        self.client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(
                size=self.vectore_dimensions,
                distance=VECTOR_DISTANCE
            )
        )

    def insert_vectors_in_collection(
        self: Self,
        points: List[PointStruct],
        collection_name: str
    ) -> None:
        if not self.client.collection_exists(collection_name):
            self.create_collection(collection_name)

        self.client.upload_points(
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
