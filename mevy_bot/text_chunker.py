from typing import Self, List

import tiktoken
from langchain_text_splitters import CharacterTextSplitter


class TextChunker:

    CHUNK_SIZE=1024
    CHUNK_OVERLAP=200

    def split_in_chunks(self: Self, text: str) -> List[str]:
        text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
            model_name="gpt-4o-mini",
            separator="\n",
            chunk_size=self.CHUNK_SIZE,
            chunk_overlap=self.CHUNK_OVERLAP
        )
        return text_splitter.split_text(text)
    
    def split_text_into_chunks(self, text):
        tokenizer = tiktoken.encoding_for_model("gpt-4o-mini")
        tokens = tokenizer.encode(text)

        chunks = []
        for i in range(0, len(tokens), self.CHUNK_SIZE):
            # Create a chunk of tokens
            token_chunk = tokens[i:i + self.CHUNK_SIZE]

            # Decode the chunk of tokens back into text
            text_chunk = tokenizer.decode(token_chunk)

            # Append the text chunk to the list of chunks
            chunks.append(text_chunk)
        return chunks
