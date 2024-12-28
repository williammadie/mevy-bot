import logging

from dotenv import load_dotenv
from langchain_ollama import OllamaEmbeddings

from mevy_bot.source_collection.source_inventory import SourceInventory
from mevy_bot.source_collection.source_retriever import SourceRetriever
from mevy_bot.vector_store.vector_store import VectorStore
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s (line %(lineno)d): %(message)s'
)
logger = logging.getLogger(__package__)


def main() -> None:
    logger.setLevel(logging.INFO)
    #source_inventory = SourceInventory()

    #source_retriever = SourceRetriever(source_inventory)
    #source_retriever.download_all()

    # OpenAI embedding model costs money :(
    #embedding_model = OpenAIEmbeddings()

    # Too slow locally
    #embedding_model = OllamaEmbeddings(
    #    model="llama3",
    #)

    embedding_model = OllamaEmbeddings(
        model="all-minilm"
    )

    vector_store = VectorStore(embedding_model)
    #vector_store.erase_store_on_disk()
    #vector_store.build_from_data_storage_files()
    #vector_store.write_on_disk()
    vector_store.build_from_disk()
    vector_store.search_in_store("Quelles sont les modalités de vente d'un bien immobilier ?")
    #vector_store.erase_store_on_disk()



if __name__ == '__main__':
    main()
