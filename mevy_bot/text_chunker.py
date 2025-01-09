from typing import Self, List

from langchain_text_splitters import CharacterTextSplitter


class TextChunker:

    CHUNK_SIZE=1000

    def split_in_chunks(self: Self, text: str) -> List[str]:
        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=self.CHUNK_SIZE,
            chunk_overlap=200,
            length_function=len
        )
        return text_splitter.split_text(text)
