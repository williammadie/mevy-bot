from typing import Self, List, Any
from abc import ABC, abstractmethod

from qdrant_client.models import ScoredPoint

from mevy_bot.vector_store.vector_store import VectorStore


class QueryHandler(ABC):

    def __init__(
        self: Self,
        vector_store: VectorStore,
        llm_model: Any
    ) -> None:
        self.vector_store: VectorStore = vector_store
        self.llm_model: Any = llm_model

    @abstractmethod
    def generate_response_with_context(self: Self, question: str, collection_name: str) -> str:
        pass

    def retrieve_context_documents(self: Self, question: str, collection_name: str) -> List[ScoredPoint]:
        """ Retrieve proper context from vector store """
        return self.vector_store.search_in_store(question, collection_name)

    def build_system_prompt(self: Self) -> str:
        return """
        You are an IEEE830 expert whose goal is to help stakeholders in a software
        development project. Answer only based on the given context elements.

        If you don't know, don't answer. When you answer, precise the sources you used
        like the reference document and page.
        """
    
    def build_system_prompt_legacy(self: Self) -> str:
        return """
        Tu es un assistant juridique et fiscal dédié aux propriétaires bailleurs en France.
        Réponds uniquement à partir des éléments du contexte fournis.
        
        Si tu ne sais pas, ne réponds pas. Lorsque tu réponds, indique les numéros, noms
        et dates des lois ou sources utilisées pour assurer la précision et la fiabilité
        des informations fournies.
        """

    def build_user_prompt(self: Self, question: str, context: str) -> str:
        return f"Basing on this information: '{context}', answer the following question '{question}'"

    def build_user_prompt_legacy(self: Self, question: str, context: str) -> str:
        return f"En te basant sur ces informations: '{context}', réponds à la question '{question}'"
