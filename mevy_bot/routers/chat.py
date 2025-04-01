import logging
import asyncio

from fastapi import APIRouter, WebSocket

from mevy_bot.models.openai import OpenAIModelFactory
from mevy_bot.vector_store.qdrant_collection import QdrantCollection
from mevy_bot.rewriter.openai_rewriter import OpenAIRewriter
from mevy_bot.vector_store.vector_store import VectorStore
from mevy_bot.generator.openai_generator import OpenAIGenerator


router = APIRouter(prefix="/chat", tags=["Chat"])

logger = logging.getLogger()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        user_query = await websocket.receive_text()  # Receive message from client
        logger.info("Received following user query: %s", user_query)

        logger.info("Starting chat operation...")

        embedding_model_info = OpenAIModelFactory.text_embedding_3_small()
        generator_model_info = OpenAIModelFactory.gpt4o_mini()

        store_client = QdrantCollection(embedding_model_info.vector_dimensions)
        vector_store = VectorStore(
            store_client,
            embedding_model_info,
            generator_model_info
        )
        collection_name = "mevy_bot"

        rewriter = OpenAIRewriter(generator_model_info.name)
        rewrited_user_query = rewriter.rewrite_user_query(user_query)
        logger.debug("""User query:
            %s

            Rewrited query:

            %s
            """,
                     user_query,
                     rewrited_user_query)

        context = vector_store.search_in_store(
            rewrited_user_query, collection_name)
        logger.debug("Context:\n\n%s", context)

        generator = OpenAIGenerator(generator_model_info, vector_store)

        for chunk in generator.generate_response_with_context_stream(
                rewrited_user_query, collection_name):
            await websocket.send_text(chunk)

        await websocket.send_text("[END]")  # Indicate end of response
