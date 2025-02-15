import os
import argparse
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
    args = parser.parse_args()
    args.func(args)


def do_embed(args) -> None:
    embed(
        args.collection_name,
        args.predict_only
    )

def do_collect(args) -> None:
    collect()


def collect() -> None:
    logger.info("Starting data collection...")
    source_inventory = SourceInventory()
    source_retriever = SourceRetriever(source_inventory)
    source_retriever.clear_data_store_auto()
    source_retriever.download_all()


def embed(
    collection_name: str,
    predict_only: bool
) -> None:
    if predict_only:
        logger.info("Predicting cost of embedding operation...")
    else:
        logger.info("Starting embedding operation...")

    if not collection_name:
        raise ValueError("collection_name cannot be None")

    embedding_model_info = OpenAIModelFactory.text_embedding_3_small()
    generator_model_info = OpenAIModelFactory.gpt4o_mini()

    store_client = QdrantCollection(embedding_model_info.vector_dimensions)
    vector_store = VectorStore(
        store_client,
        embedding_model_info,
        generator_model_info
    )
    vector_store.predict_costs_of_store_building()
    
    if not predict_only:
        vector_store.build_from_data_storage_files(collection_name)


def chat() -> None:
    logger.info("Starting chat operation...")
    user_query = "L'Etat a-t-il le droit d'exproprier un propriétaire ?"

    embedding_model_info = OpenAIModelFactory.text_embedding_3_small()
    generator_model_info = OpenAIModelFactory.gpt4o_mini()

    store_client = QdrantCollection(embedding_model_info.vector_dimensions)
    vector_store = VectorStore(
        store_client,
        embedding_model_info,
        generator_model_info
    )
    collection_name = "mevy-bot-1024_0.2"

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

########################################### CLI Settings Section ###########################################


parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(
    title="commands", help="bot operations"
)

collect_parser = subparsers.add_parser(
    'collect', help="collect data from predefined sources")
collect_parser.set_defaults(func=do_collect)

embed_parser = subparsers.add_parser(
    'embed', help="embed collected sources and store the embeddings in the bot vector store")
embed_parser.add_argument(
    "-c",
    "--collection-name",
    help="the name of the target collection in the vector store",
    type=str
)
embed_parser.add_argument(
    "--predict-only",
    help="if this option is used, the program will only predict the cost of \
        embeddings without doing the actual operation.",
    default=False,
    action=argparse.BooleanOptionalAction
)
embed_parser.set_defaults(func=do_embed)

chat_parser = subparsers.add_parser('chat', help="ask a question to mevy bot")
chat_parser.set_defaults(func=chat)


if __name__ == '__main__':
    main()
