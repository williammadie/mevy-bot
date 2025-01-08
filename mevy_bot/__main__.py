import logging

from dotenv import load_dotenv
from langchain_ollama import OllamaEmbeddings
from openai import OpenAI

from mevy_bot.source_collection.source_inventory import SourceInventory
from mevy_bot.source_collection.source_retriever import SourceRetriever
from mevy_bot.vector_store.vector_store import VectorStore
from mevy_bot.query_handler.openai_query_handler import OpenAIQueryHandler

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
    vector_store.build_from_data_storage_files()
    #vector_store.write_on_disk()
    #vector_store.build_from_disk()
    #res = vector_store.search_in_store("Tous les citoyens sont-ils égaux devant la loi ?")
    #print(res)
    #vector_store.erase_store_on_disk()

    llm_model = OpenAI()

    #query_handler = OpenAIQueryHandler(vector_store, llm_model)
    #completion = query_handler.generate_response("Tous les citoyens sont-ils égaux devant la loi ?")
    #print(completion)


if __name__ == '__main__':
    main()
