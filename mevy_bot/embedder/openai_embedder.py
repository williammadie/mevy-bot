
from typing import Self
from decimal import Decimal

from openai import OpenAI
from openai.types import CreateEmbeddingResponse

from mevy_bot.models.openai import EmbeddingModel


class OpenAIEmbedder:

    def __init__(
        self: Self,
        embedding_model: EmbeddingModel
    ) -> None:
        self.embedding_model = embedding_model
        self.client = OpenAI()

    def generate_embeddings(self: Self, text_chunk: str) -> CreateEmbeddingResponse:
        return self.client.embeddings.create(
            input=text_chunk,
            model=self.embedding_model.name
        )
