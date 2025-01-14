from dataclasses import dataclass
from decimal import Decimal


@dataclass
class GenerativeAiModel:
    name: str
    max_tokens_input: int
    price_per_1k_input_tokens: Decimal


@dataclass
class EmbeddingModel(GenerativeAiModel):
    vector_dimensions: int


@dataclass
class ChatModel(GenerativeAiModel):
    max_tokens_output: int
    price_per_1k_output_tokens: Decimal


class OpenAIModelFactory:

    @staticmethod
    def text_embedding_3_small() -> EmbeddingModel:
        # Source: https://platform.openai.com/docs/guides/embeddings#embedding-models
        return EmbeddingModel(
            name="text-embedding-3-small",
            max_tokens_input=8191,
            vector_dimensions=1536,
            price_per_1k_input_tokens=Decimal("0.000020")
        )

    @staticmethod
    def text_embedding_3_large() -> EmbeddingModel:
        # Source: https://platform.openai.com/docs/guides/embeddings#embedding-models
        return EmbeddingModel(
            name="text-embedding-3-large",
            max_tokens_input=8191,
            vector_dimensions=3072,
            price_per_1k_input_tokens=Decimal("0.000130")
        )

    @staticmethod
    def gpt4o_mini() -> ChatModel:
        # Source: https://openai.com/index/gpt-4o-mini-advancing-cost-efficient-intelligence/
        return ChatModel(
            name="gpt-4o-mini",
            max_tokens_input=128_000,
            max_tokens_output=16_000,
            price_per_1k_input_tokens=Decimal("0.000150"),
            price_per_1k_output_tokens=Decimal("0.000600")
        )
