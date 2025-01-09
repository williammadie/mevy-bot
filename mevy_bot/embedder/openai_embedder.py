
from typing import Self
from decimal import Decimal

from openai import OpenAI
from openai.types import CreateEmbeddingResponse


class OpenAIEmbedder:

    PRICE_PER_1K_TOKENS: Decimal = Decimal('0.000020')

    def __init__(
        self: Self,
        embedding_model_name: str = "text-embedding-3-small"
    ) -> None:
        self.embedding_model_name = embedding_model_name
        self.client = OpenAI()

    def generate_embeddings(self: Self, text_chunk: str) -> CreateEmbeddingResponse:
        return self.client.embeddings.create(
            input=text_chunk,
            model=self.embedding_model_name
        )
