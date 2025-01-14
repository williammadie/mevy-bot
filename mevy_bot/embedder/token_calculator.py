from typing import Self, List, Tuple

import tiktoken

from mevy_bot.models.openai import ChatModel


class TokenCalculator:

    def __init__(self: Self, chat_model: ChatModel) -> None:
        self.chat_model = chat_model

    def nb_tokens_in_text_chunk(self: Self, text_chunk: str) -> int:
        tokenizer = tiktoken.encoding_for_model(self.chat_model.name)
        tokenized_text: List[int] = tokenizer.encode(text_chunk)
        return len(tokenized_text)

    def nb_tokens_nb_chars(
        self: Self,
        text: str,
    ) -> Tuple[int, int]:
        nb_chars = len(text)
        nb_tokens = self.nb_tokens_in_text_chunk(text)
        return nb_tokens, nb_chars
