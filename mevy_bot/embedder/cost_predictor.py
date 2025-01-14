import logging
from typing import Self
from decimal import Decimal

l = logging.getLogger(__name__)

class CostPredictor:
    """
    A helper class for predicting the cost of generating the embeddings
    for n chunks of text.

    Basic rules:

    - 1 token ~= 4 chars
    - 100 tokens ~= 75 words
    source: https://help.openai.com/en/articles/4936856-what-are-tokens-and-how-to-count-them

    """
    def __init__(self: Self, price_per_1k_input_tokens: Decimal) -> None:
        self.price_per_1k_input_tokens: Decimal = price_per_1k_input_tokens

    def calculate_cost_based_on_chunk_size(
        self: Self,
        nb_chunks: int,
        chunk_size: int
    ) -> Decimal:
        nb_tokens = Decimal(nb_chunks * chunk_size / 4)
        return self.calculate_cost_based_on_token_count(
            nb_tokens
        )

    def calculate_cost_based_on_token_count(
        self: Self,
        nb_tokens: Decimal
    ) -> Decimal:
        return nb_tokens * self.price_per_1k_input_tokens / 1000

