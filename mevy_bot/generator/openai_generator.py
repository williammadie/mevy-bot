import logging
from typing import Self, List, Generator

from qdrant_client.models import ScoredPoint

from mevy_bot.generator.generator import ResponseGenerator
from mevy_bot.models.openai import ChatModel
from mevy_bot.vector_store.vector_store import VectorStore
from mevy_bot.gateways.openai_gateway import OpenAIGateway

l = logging.getLogger(__name__)


class OpenAIGenerator(ResponseGenerator):

    def __init__(
        self: Self,
        chat_model_info: ChatModel,
        vector_store: VectorStore,
    ) -> None:
        super().__init__(vector_store)
        self.chat_model_info = chat_model_info
        self.openai_gateway = OpenAIGateway(chat_model_info.name)

    def generate_response_with_context(self: Self, question: str, collection_name: str) -> str:
        context_documents = self.retrieve_context_documents(
            question, collection_name)
        context = self.refine_retrieved_context(context_documents)
        system_prompt = self.build_system_prompt()
        user_prompt = self.build_user_prompt(question, context)
        return self.openai_gateway.send_query(system_prompt, user_prompt)

    def generate_response_with_context_stream(
        self: Self, question: str, collection_name: str
    ) -> Generator:
        context_documents = self.retrieve_context_documents(
            question, collection_name)
        context = self.refine_retrieved_context(context_documents)
        system_prompt = self.build_system_prompt()
        user_prompt = self.build_user_prompt(question, context)

        for chunk in self.openai_gateway.send_query_stream(system_prompt, user_prompt):
            yield chunk

    def refine_retrieved_context(self: Self, documents: List[ScoredPoint]) -> str:
        context = ""
        for doc in documents:
            if doc.payload is not None and doc.score > 0.6:
                doc_content = doc.payload.get('text')
                context += f'{doc_content}\n\n'

        if not context:
            context = "Aucune information du contexte ne permet de répondre à cette demande."

        return context

    def list_documents_from_retrieved_context(
        self: Self,
        retrieved_documents: List[ScoredPoint]
    ) -> List[str]:
        docs = []
        for doc in retrieved_documents:
            if doc.payload is not None:
                doc_content = doc.payload.get('text')
                docs.append(doc_content)

        return docs
