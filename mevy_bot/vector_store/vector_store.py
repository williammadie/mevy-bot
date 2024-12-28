import logging
import os
from functools import wraps
from typing import Self, List

from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.embeddings import Embeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

from mevy_bot.exceptions.unsupported_file_type_error import UnsupportedFileTypeError
from mevy_bot.exceptions.vector_store_not_initialized_error import VectorStoreNotInitializedError
from mevy_bot.path_finder import PathFinder

l = logging.getLogger(__name__)


def fail_on_empty_db(func):
    """Decorator to ensure the vector store is initialized before method execution."""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not hasattr(self, "db") or self.db is None:
            raise VectorStoreNotInitializedError(
                "Vector store is not initialized."
            )
        return func(self, *args, **kwargs)
    return wrapper


class VectorStore:

    def __init__(self: Self, embedding_model: Embeddings) -> None:
        self.embedding_model: Embeddings = embedding_model
        self.db: FAISS
        self.ensure_directories_exist()

    def ensure_directories_exist(self) -> None:
        """ Create mandatory directories if missing """
        os.makedirs(PathFinder.data_storage(), exist_ok=True)
        os.makedirs(PathFinder.vector_store(), exist_ok=True)

    def build_from_data_storage_files(self: Self) -> None:
        """ Build a vector store from PDF files in data_storage dir """
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
        self.db = FAISS.from_documents(all_docs, self.embedding_model)
        l.info("Vector store successfully built.")

    def build_from_disk(self: Self) -> None:
        """
        Load the vector store state from disk.
        """
        vector_store_dir = PathFinder.vector_store()
        l.info("Building vector store from disk (%s)...", vector_store_dir)
        self.db = FAISS.load_local(
            vector_store_dir,
            self.embedding_model,
            allow_dangerous_deserialization=True
        )
        l.info("Vector store successfully built.")

    @fail_on_empty_db
    def write_on_disk(self: Self) -> None:
        """
        Save the current state of the vector store to disk.
        """
        vector_store_dir = PathFinder.vector_store()
        l.info("Writing vector store on disk (%s)...", vector_store_dir)
        self.db.save_local(vector_store_dir)
        l.info("Vector store written on disk.")

    @fail_on_empty_db
    def search_in_store(self: Self, search_pattern: str) -> None:
        """ Search a string pattern in vector store """
        retriever = self.db.as_retriever()
        retrieved_documents = retriever.invoke(search_pattern)
        print(retrieved_documents)
        print(retrieved_documents[0].page_content)

    def erase_store_on_disk(self: Self) -> None:
        """ Delete all information stored in vector_store dir """
        l.info("Erasing store data written on disk...")
        vector_store_dir = PathFinder.vector_store()
        files_in_store_dir: List[str] = os.listdir(vector_store_dir)
        if not files_in_store_dir:
            l.warning("Operation aborted: no store data written on disk.")
            return

        for filename in files_in_store_dir:
            filepath = os.path.join(vector_store_dir, filename)
            os.remove(filepath)
        l.info("Store data on disk successfully erased.")
