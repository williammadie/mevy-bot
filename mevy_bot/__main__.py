import os
import logging
from logging.handlers import TimedRotatingFileHandler

from dotenv import load_dotenv
from openai import OpenAI

from mevy_bot.path_finder import PathFinder
from mevy_bot.source_collection.source_inventory import SourceInventory
from mevy_bot.source_collection.source_retriever import SourceRetriever
from mevy_bot.vector_store.vector_store import VectorStore
from mevy_bot.query_handler.openai_query_handler import OpenAIQueryHandler
from mevy_bot.vector_store.qdrant_collection import QdrantCollection

load_dotenv()

LOGGING_FORMAT = '%(asctime)s [%(levelname)s] %(name)s (line %(lineno)d): %(message)s'
logging.basicConfig(
    level=logging.INFO,
    format=LOGGING_FORMAT
)
logger = logging.getLogger()

logs_dir = PathFinder.log_dirpath()
os.makedirs(logs_dir, exist_ok=True)
rotation_logging_handler = TimedRotatingFileHandler(
    filename=os.path.join(logs_dir, 'log'),
    interval=1,
    when='D',
    backupCount=7
)
rotation_logging_handler.setFormatter(logging.Formatter(LOGGING_FORMAT))
rotation_logging_handler.setLevel(logging.INFO)
logger.addHandler(rotation_logging_handler)
logger.setLevel(logging.INFO)

def main() -> None:
    # source_inventory = SourceInventory()

    # source_retriever = SourceRetriever(source_inventory)
    # source_retriever.download_all()

    store_client = QdrantCollection()
    vector_store = VectorStore(store_client)
    collection_name = "mevy-bot"
    vector_store.build_from_data_storage_files(collection_name)
    #user_query = "What is the most important concept of the IEEE830 standard?"
    #res = vector_store.search_in_store(
    #    user_query,
    #    collection_name
    #)
    #logger.info(res)

    #llm_model = OpenAI()
    #query_handler = OpenAIQueryHandler(vector_store, llm_model)
    #completion = query_handler.generate_response_with_context(user_query, collection_name)
    #print(completion)


if __name__ == '__main__':
    main()
