from typing import Self, List

from langchain_text_splitters import CharacterTextSplitter


class FileSplitter:

    def split_in_chunks(self: Self, text: str) -> List[str]:
        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        return text_splitter.split_text(text)
