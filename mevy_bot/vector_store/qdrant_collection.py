import os
import logging
from typing import Self, List, Sequence

from http import HTTPStatus

from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import (
    ResponseHandlingException,
    UnexpectedResponse
)
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    ScoredPoint,
    Filter,
    FilterSelector,
    FieldCondition,
    MatchValue
)

l = logging.getLogger()

VECTOR_DISTANCE = Distance.COSINE


class QdrantCollection():

    URL = os.getenv('QDRANT_DB_URL')

    def __init__(self: Self, vector_dimensions: int) -> None:
        self.vectore_dimensions = vector_dimensions
        self.client = self.get_qdrant_client()

    @staticmethod
    def get_qdrant_client() -> QdrantClient:
        return QdrantClient(url=QdrantCollection.URL)

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

    def delete_vectors_for_source(
            self: Self,
            collection_name: str,
            source_name: str) -> None:
        try:
            self.client.delete(
                collection_name=collection_name,
                points_selector=FilterSelector(
                    filter=Filter(
                        must=[
                            FieldCondition(
                                key="source",
                                match=MatchValue(value=source_name)
                            ),
                        ],
                    )
                )
            )
        except UnexpectedResponse as exc:
            if exc.status_code == HTTPStatus.NOT_FOUND:
                l.info("Cannot delete vectors, reason: %s", exc.content)

    @staticmethod
    def delete_collection(collection_name: str) -> None:
        client = QdrantCollection.get_qdrant_client()
        client.delete_collection(collection_name=collection_name)

    @staticmethod
    def healthcheck() -> bool:
        client = QdrantCollection.get_qdrant_client()
        try:
            client.info()
            return True
        except ResponseHandlingException:
            return False
