import os
import logging
from typing import Self, List, Sequence

from http import HTTPStatus

from qdrant_client import AsyncQdrantClient
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
    def get_qdrant_client() -> AsyncQdrantClient:
        return AsyncQdrantClient(url=QdrantCollection.URL)

    async def create_collection(self: Self, name: str) -> None:
        await self.client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(
                size=self.vectore_dimensions,
                distance=VECTOR_DISTANCE
            )
        )

    async def insert_vectors_in_collection(
        self: Self,
        points: List[PointStruct],
        collection_name: str
    ) -> None:
        if not self.client.collection_exists(collection_name):
            await self.create_collection(collection_name)

        self.client.upload_points(
            collection_name=collection_name,
            wait=True,
            points=points
        )

    async def search_in_collection(
        self: Self,
        collection_name: str,
        embeddings: Sequence[float],
        max_output_documents: int = 3
    ) -> List[ScoredPoint]:
        return await self.client.search(
            collection_name=collection_name,
            query_vector=embeddings,
            limit=max_output_documents
        )

    async def delete_vectors_for_source(
            self: Self,
            collection_name: str,
            source_name: str) -> None:
        try:
            await self.client.delete(
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
    async def delete_collection(collection_name: str) -> None:
        client = QdrantCollection.get_qdrant_client()
        await client.delete_collection(collection_name=collection_name)

    @staticmethod
    async def healthcheck() -> bool:
        client = QdrantCollection.get_qdrant_client()
        try:
            await client.info()
            return True
        except ResponseHandlingException:
            return False
