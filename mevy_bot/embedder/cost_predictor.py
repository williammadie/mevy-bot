from typing import Self
from decimal import Decimal

from mevy_bot.embedder.openai_embedder import OpenAIEmbedder


class CostPredictor:
    """
    A helper class for predicting the cost of generating the embeddings
    for n chunks of text.

    Basic rules:

    - 1 token ~= 4 chars
    - 100 tokens ~= 75 words
    source: https://help.openai.com/en/articles/4936856-what-are-tokens-and-how-to-count-them

    """

    @staticmethod
    def calculate_cost_based_on_chunk_size(
        nb_chunks: int,
        chunk_size: int,
        price_per_1k_tokens: Decimal = OpenAIEmbedder.PRICE_PER_1K_TOKENS
    ) -> Decimal:
        nb_tokens = Decimal(nb_chunks * chunk_size / 4)
        return CostPredictor.calculate_cost_based_on_token_count(
            nb_tokens,
            price_per_1k_tokens
        )

    @staticmethod
    def calculate_cost_based_on_token_count(
        nb_tokens: Decimal,
        price_per_1k_tokens: Decimal = OpenAIEmbedder.PRICE_PER_1K_TOKENS
    ) -> Decimal:
        return nb_tokens * price_per_1k_tokens / 1000
