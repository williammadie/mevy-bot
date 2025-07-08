import logging
from typing import Self, List, AsyncGenerator

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

    async def generate_social_response_stream(self: Self, question: str, meta_knowledge: str) -> AsyncGenerator:
        system_prompt = self.build_social_system_prompt()
        user_prompt = self.build_user_prompt(question, meta_knowledge)
        for chunk in self.openai_gateway.send_query_stream(system_prompt, user_prompt):
            yield chunk

    def generate_response_with_context(self: Self, question: str, collection_name: str) -> str:
        context_documents = self.retrieve_context_documents(
            question, collection_name)
        context = self.refine_retrieved_context(context_documents)
        system_prompt = self.build_expert_system_prompt()
        user_prompt = self.build_user_prompt(question, context)
        return self.openai_gateway.send_query(system_prompt, user_prompt)

    async def generate_response_with_context_stream(
        self: Self, question: str, collection_name: str
    ) -> AsyncGenerator:
        context_documents = await self.retrieve_context_documents(
            question, collection_name)
        context = self.refine_retrieved_context(context_documents)
        system_prompt = self.build_expert_system_prompt()
        user_prompt = self.build_user_prompt(question, context)

        l.info(user_prompt)

        for chunk in self.openai_gateway.send_query_stream(system_prompt, user_prompt):
            yield chunk

    def refine_retrieved_context(self: Self, documents: List[ScoredPoint]) -> str:
        context = ""
        for doc in documents:
            if doc.payload is not None:
                if doc.score > 0.6:
                    doc_content = doc.payload.get('text')
                    context += f'{doc_content}\n\n'
                else:
                    # We allow chunks related to meta-questions to have a smaller score
                    # as these questions are highly generic and are mostly noise for
                    # the semantic search algorithm
                    doc_type = doc.payload.get('type')
                    if doc_type == "meta" and doc.score > 0.3:
                        doc_content = doc.payload.get('text')
                        context += f'{doc_content}\n\n'

        if not context:
            context = """
            <knowledge>
            Aucune information ne permet de répondre à cette demande.
            
            Une recherche Internet peut être effectuée si possible. Si aucune
            information pertinente n'en ressort, demandez à l'utilisateur
            de contacter un opérateur Mevy. 
            </knowledge>
            """

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
