import logging
import os
from typing import Self
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.embeddings import Embeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

from mevy_bot.exceptions.unsupported_file_type_error import UnsupportedFileTypeError
from mevy_bot.path_finder import PathFinder

l = logging.getLogger(__name__)


class VectorStoreBuilder:

    def __init__(self: Self, embedding_model: Embeddings) -> None:
        self.embedding_model: Embeddings = embedding_model
        self.vector_store: FAISS = self.build_from_data_storage_files()

    def build_from_data_storage_files(self: Self) -> FAISS:
        l.info("Building vector store from data storage files...")
        all_docs = []
        storage_dir = PathFinder.data_storage()
        for filename in os.listdir(storage_dir):
            if not filename.endswith('.pdf'):
                raise UnsupportedFileTypeError(filename)

            filepath = os.path.join(storage_dir, filename)
            loader = PyPDFLoader(filepath)
            pages = loader.load()

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=1000
            )
            docs = text_splitter.split_documents(pages)

            all_docs.extend(docs)
        vector_store = FAISS.from_documents(all_docs, self.embedding_model)
        l.info("Vector store successfully built!")
        return vector_store

    def write_on_disk(self: Self) -> None:
        """
        Save the current state of the vector store to disk.
        """
        vector_store_dir = PathFinder.vector_store()
        filepath = os.path.join(vector_store_dir, "vector_store_index")
        l.info("Writing vector store on disk (%s)...", filepath)
        self.vector_store.save_local(filepath)
        l.info("Operation completed")

    def read_from_disk(self: Self) -> None:
        """
        Load the vector store state from disk.
        """
        vector_store_dir = PathFinder.vector_store()
        filepath = os.path.join(vector_store_dir, "vector_store_index")
        l.info("Reading vector store from disk (%s)...", filepath)
        self.vector_store = FAISS.load_local(
            filepath,
            self.embedding_model,
            allow_dangerous_deserialization=True
        )
        l.info("Operation completed")
