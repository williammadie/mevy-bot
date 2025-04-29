from typing import Self, List
from abc import ABC, abstractmethod

from qdrant_client.models import ScoredPoint

from mevy_bot.vector_store.vector_store import VectorStore


class ResponseGenerator(ABC):

    MODEL_TEMPERATURE = 0

    def __init__(
        self: Self,
        vector_store: VectorStore
    ) -> None:
        self.vector_store: VectorStore = vector_store

    @abstractmethod
    def generate_response_with_context(self: Self, question: str, collection_name: str) -> str:
        pass

    async def retrieve_context_documents(self: Self, question: str, collection_name: str) -> List[ScoredPoint]:
        """ Retrieve proper context from vector store """
        return await self.vector_store.search_in_store(question, collection_name)

    def build_system_prompt(self: Self) -> str:
        return """
        Vous êtes un spécialiste des questions juridique et fiscale en France.
        
        Votre objectif est de répondre aux questions de propriétaires bailleurs
        en France en vous basant uniquement sur le contexte fourni lors de la
        demande.
        
        Si vous n'êtes pas en mesure de répondre uniquement à partir du informations
        fournies, vous ne devez pas répondre.
        
        Si vous êtes en mesure de proposer un début d'élément de réponse, mais que vous
        jugez votre réponse trop peu fournie, répondez en indiquant de contacter un
        opérateur Mevy pour compléter la demande.
                
        Lorsque vous répondez, indiquez les numéros, noms et dates des lois ou sources utilisées
        pour assurer la transparence, la précision et la fiabilité des informations de ton contexte.
        """

    def build_user_prompt(self: Self, question: str, context: str) -> str:
        return f"En vous basant sur ces informations: '{context}', répondez à la question suivante: '{question}'"
