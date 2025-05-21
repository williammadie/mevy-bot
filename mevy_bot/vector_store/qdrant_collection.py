import os
import logging
import inspect
from typing import Self, List, Sequence, Callable, Coroutine
from functools import wraps
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


def ensure_collection_exists(method: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
    @wraps(method)
    async def wrapper(self, *args, **kwargs):
        sig = inspect.signature(method)
        bound_args = sig.bind(self, *args, **kwargs)
        bound_args.apply_defaults()

        collection_name = bound_args.arguments.get("collection_name")
        l.info("Using collection_name: %s", collection_name)
        if not collection_name:
            raise ValueError("collection_name is required for this operation")

        try:
            if not await self.client.collection_exists(collection_name):
                await self.create_collection(collection_name)
        except Exception as e:
            l.error("Failed to check or create collection '%s': %s",
                    collection_name, e)
            raise

        return await method(self, *args, **kwargs)
    return wrapper

class QdrantCollection():

    URL = os.getenv('QDRANT_DB_URL')

    def __init__(self: Self, vector_dimensions: int) -> None:
        self.vector_dimensions = vector_dimensions
        self.client = self.get_qdrant_client()

    @staticmethod
    def get_qdrant_client() -> AsyncQdrantClient:
        return AsyncQdrantClient(url=QdrantCollection.URL)

    async def create_collection(self: Self, name: str) -> None:
        await self.client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(
                size=self.vector_dimensions,
                distance=VECTOR_DISTANCE
            )
        )

    @ensure_collection_exists
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

    @ensure_collection_exists
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

    @ensure_collection_exists
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
