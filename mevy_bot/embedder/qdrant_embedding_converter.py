import logging
import uuid
from abc import ABC
from typing import Self, List
from datetime import datetime

from qdrant_client.http.models import PointStruct

from mevy_bot.embedder.openai_embedder import OpenAIEmbedder

l = logging.getLogger(__name__)


class QdrantEmbeddingConverter(ABC):

    def __init__(
        self: Self,
        embedder: OpenAIEmbedder
    ) -> None:
        self.embedder = embedder

    def get_embeddings_text_chunk(
        self: Self,
        text_chunk: str,
        filename: str
    ) -> PointStruct:
        response = self.embedder.generate_embeddings(text_chunk)

        point_embeddings = response.data[0].embedding
        point_id = str(uuid.uuid4())

        now = datetime.now()
        str_now = now.strftime("%m-%d-%Y")
        return PointStruct(
            id=point_id,
            vector=point_embeddings,
            payload={
                "text": text_chunk,
                "source": filename,
                "last_update_date": str_now,
                **({"type": "meta"} if "meta-questions" in filename else {})
            }
        )

    def get_embeddings_text_chunks(
        self: Self,
        text_chunks: List[str],
        filename: str
    ) -> List[PointStruct]:
        nb_chunks = len(text_chunks)
        points = []
        for chunk_index, text_chunk in enumerate(text_chunks):
            point = self.get_embeddings_text_chunk(text_chunk, filename)
            points.append(point)
            l.info("%d/%d chunks have been processed.",
                   chunk_index + 1, nb_chunks)
        return points
