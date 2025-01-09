import logging

from dotenv import load_dotenv
from langchain_ollama import OllamaEmbeddings
from openai import OpenAI

from mevy_bot.source_collection.source_inventory import SourceInventory
from mevy_bot.source_collection.source_retriever import SourceRetriever
from mevy_bot.vector_store.vector_store import VectorStore
from mevy_bot.query_handler.openai_query_handler import OpenAIQueryHandler
from mevy_bot.vector_store.qdrant_collection import QdrantCollection

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s (line %(lineno)d): %(message)s'
)
logger = logging.getLogger(__package__)


def main() -> None:
    logger.setLevel(logging.INFO)
    # source_inventory = SourceInventory()

    # source_retriever = SourceRetriever(source_inventory)
    # source_retriever.download_all()

    store_client = QdrantCollection()
    vector_store = VectorStore(store_client)
    collection_name = "mevy-chatbot"
    vector_store.build_from_data_storage_files(collection_name)
    res = vector_store.search_in_store(
        "Tous les citoyens sont-ils égaux devant la loi ?",
        collection_name
    )
    print(res)

    # llm_model = OpenAI()
    # query_handler = OpenAIQueryHandler(vector_store, llm_model)
    # completion = query_handler.generate_response("Tous les citoyens sont-ils égaux devant la loi ?")
    # print(completion)


if __name__ == '__main__':
    main()
