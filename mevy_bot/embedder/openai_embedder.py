
from typing import Self

from openai import Embedding

class OpenAIEmbedder:

    def __init__(
        self: Self,
        embedding_model_name: str = "text-embedding-ada-002"
    ) -> None:
        self.embedding_model_name = embedding_model_name

    def generate_embeddings(self: Self, text_chunk: str) -> dict:
        return Embedding.create(
            input=text_chunk,
            model=self.embedding_model_name
        )