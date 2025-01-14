import re
import logging
from typing import Self, List

import semchunk
import tiktoken
from langchain_text_splitters import CharacterTextSplitter

from mevy_bot.models.openai import EmbeddingModel, ChatModel
from mevy_bot.file_reader import FileReader

l = logging.getLogger(__name__)


class TextChunker:
    CHUNK_SIZE = 1024
    CHUNK_OVERLAP = 200

    def __init__(
        self: Self,
        embedding_model: EmbeddingModel,
        chat_model: ChatModel
    ) -> None:
        self.embedding_model = embedding_model
        self.chat_model = chat_model

    def split_in_chunks(self: Self, text: str) -> List[str]:
        text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
            model_name=self.chat_model.name,
            separator="\n",
            chunk_size=self.CHUNK_SIZE,
            chunk_overlap=self.CHUNK_OVERLAP
        )
        return text_splitter.split_text(text)

    def split_text_into_chunks(self, text: str, max_tokens: int) -> List[str]:
        if max_tokens > self.embedding_model.max_tokens_input:
            l.error(
                "max_tokens (%d) is bigger than model max input tokens (%d)",
                max_tokens,
                self.embedding_model.max_tokens_input
            )
            raise ValueError(
                f"max_tokens ({max_tokens}) > max_tokens_input ({self.embedding_model.max_tokens_input})")

        tokenizer = tiktoken.encoding_for_model(self.chat_model.name)
        tokenized_text: List[int] = tokenizer.encode(text)

        chunks = []
        current_chunk = []
        current_length = 0

        for token in tokenized_text:
            current_chunk.append(token)
            current_length += 1

            if current_length >= max_tokens:
                current_text = tokenizer.decode(current_chunk)
                chunks.append(current_text)
                current_chunk = []
                current_length = 0

        if current_chunk:
            remaining_text = tokenizer.decode(current_chunk)
            chunks.append(remaining_text)

        return chunks

    def word_splitter(self: Self, source_text: str) -> List[str]:
        # Replace multiple whitespaces
        source_text = re.sub(r"\s+", " ", source_text)
        return re.split(r"\s", source_text)  # Split by single whitespace

    def split_in_chunks_with_overlap(
        self: Self,
        text: str,
        chunk_size: int,
        overlap_fraction: float
    ) -> List[str]:
        text_words = self.word_splitter(text)
        overlap_int = int(chunk_size * overlap_fraction)
        chunks = []
        for i in range(0, len(text_words), chunk_size):
            chunk_words = text_words[max(i - overlap_int, 0): i + chunk_size]
            chunk = " ".join(chunk_words)
            chunks.append(chunk)
        return chunks

    def split_in_chunks_semchunk(
        self: Self,
        text: str,
        chunk_size: int,
        overlap_fraction: float
    ) -> List[str]:
        tokenizer = tiktoken.encoding_for_model(self.chat_model.name)
        chunker = semchunk.chunkerify(tokenizer, chunk_size)
        return chunker(text, overlap=overlap_fraction)  # type: ignore

    def chunks_from_document(
        self: Self,
        filepath: str,
        chunk_size: int,
        overlap_fraction: float
    ) -> List[str]:
        file_reader = FileReader()
        file_text = file_reader.read_text_from_pdf(filepath)

        text_chunks = self.split_in_chunks_semchunk(
            file_text,
            chunk_size,
            overlap_fraction
        )
        return text_chunks
