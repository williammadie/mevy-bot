import logging

from fastapi import APIRouter, WebSocket
from starlette.websockets import WebSocketDisconnect

from mevy_bot.models.openai import OpenAIModelFactory
from mevy_bot.vector_store.qdrant_collection import QdrantCollection
from mevy_bot.classifier.openai_classifier import OpenAIClassifier
from mevy_bot.vector_store.vector_store import VectorStore
from mevy_bot.generator.openai_generator import OpenAIGenerator
from mevy_bot.services.gdrive_service import GdriveService
from mevy_bot.database.redis_handler import RedisHandler

META_FILE_EXPIRATION_SECONDS = 86400

router = APIRouter(prefix="/chat", tags=["Chat"])

logger = logging.getLogger()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            user_query = await websocket.receive_text()  # Receive message from client
            logger.info("Received following user query: %s", user_query)

            logger.info("Starting chat operation...")

            embedding_model_info = OpenAIModelFactory.text_embedding_3_small()
            social_model_info = OpenAIModelFactory.gpt4o_mini()
            expert_model_info = OpenAIModelFactory.gpt4o_mini_search_preview()
            classifier_model_info = OpenAIModelFactory.gpt4o_mini()

            store_client = QdrantCollection(
                embedding_model_info.vector_dimensions)
            vector_store = VectorStore(
                store_client,
                embedding_model_info,
                expert_model_info
            )
            collection_name = "mevy_bot"

            # Find wether user request is relevant to chatbot domain or not
            classifier = OpenAIClassifier(classifier_model_info.name)
            query_category = classifier.classify_user_query(user_query)
            logger.info(
                "[Classification] Type de demande: %s",
                query_category
            )

            # Request is irrelevant to expert domain
            if query_category == "hors sujet":
                await websocket.send_text("Je ne peux pas répondre à cette demande.")

            # Request is social or a meta-question
            elif query_category in ["meta", "social"]:
                redis_handler = RedisHandler()
                cached_metafile = redis_handler.get("meta_file")
                if cached_metafile:
                    meta_knowledge = cached_metafile
                else:
                    gdrive_service = GdriveService()
                    meta_knowledge = gdrive_service.retrieve_meta_file()
                    redis_handler.set(
                        "meta_file",
                        meta_knowledge,
                        ex=META_FILE_EXPIRATION_SECONDS
                    )
                logger.info("Meta knowledge: %s", meta_knowledge)
                social = OpenAIGenerator(social_model_info, vector_store)
                async for chunk in social.generate_social_response_stream(user_query, meta_knowledge):
                    await websocket.send_text(chunk)

            # Request is question requiring expert knowledge
            else:
                context = await vector_store.search_in_store(
                    user_query, collection_name)
                logger.info("Context:\n\n%s", context)

                expert = OpenAIGenerator(expert_model_info, vector_store)

                async for chunk in expert.generate_response_with_context_stream(
                        user_query, collection_name):
                    await websocket.send_text(chunk)

            await websocket.send_text("[END]")  # Indicate end of response

    except WebSocketDisconnect:
        logger.warning("Client closed WebSocket.")
    except Exception as e:
        logger.error("Unexpected WebSocket error:", exc_info=e)
    finally:
        logger.info("Closing WebSocket connection.")
