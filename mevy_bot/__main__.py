import os
import logging
from logging.handlers import TimedRotatingFileHandler

from dotenv import load_dotenv
from openai import OpenAI

from mevy_bot.path_finder import PathFinder
from mevy_bot.source_collection.source_inventory import SourceInventory
from mevy_bot.source_collection.source_retriever import SourceRetriever
from mevy_bot.vector_store.vector_store import VectorStore
from mevy_bot.generator.openai_generator import OpenAIGenerator
from mevy_bot.vector_store.qdrant_collection import QdrantCollection
from mevy_bot.models.openai import OpenAIModelFactory
from mevy_bot.rewriter.openai_rewriter import OpenAIRewriter

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
    source_inventory = SourceInventory()

    source_retriever = SourceRetriever(source_inventory)
    source_retriever.download_all()
    """
    embedding_model_info = OpenAIModelFactory.text_embedding_3_small()
    generator_model_info = OpenAIModelFactory.gpt4o_mini()

    store_client = QdrantCollection(embedding_model_info.vector_dimensions)
    vector_store = VectorStore(
        store_client, embedding_model_info, generator_model_info)
    collection_name = "mevy-bot-1024_0.2"
    # vector_store.predict_costs_of_store_building()
    # vector_store.build_from_data_storage_files(collection_name)

    user_query = "L'Etat a-t-il le droit d'exproprier un propriétaire ?"
    
    
    rewriter = OpenAIRewriter(generator_model_info.name)
    rewrited_user_query = rewriter.rewrite_user_query(user_query)
    logger.info(rewrited_user_query)

    res = vector_store.search_in_store(
        user_query,
        collection_name
    )
    logger.info(res)

    generator = OpenAIGenerator(generator_model_info, vector_store)
    completion = generator.generate_response_with_context(
        rewrited_user_query, collection_name)
    print(completion)
    """


if __name__ == '__main__':
    main()
