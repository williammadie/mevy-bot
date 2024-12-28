from typing import Self, List

from langchain_openai.chat_models.base import BaseChatModel
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document

from mevy_bot.vector_store.vector_store import VectorStore


class QueryHandler:

    def __init__(
        self: Self,
        vector_store: VectorStore,
        chat_model: BaseChatModel
    ) -> None:
        self.vector_store: VectorStore = vector_store
        self.chat_model: BaseChatModel = chat_model
    
    def generate_response(self: Self, question: str) -> str:
        context = self.retrieve_context(question)
        prompt = self.build_prompt(question)
        
        docs_content = "\n\n".join(
            doc.page_content for doc in context)
        messages = prompt.invoke(
            {"question": question, "context": docs_content})
        response = self.chat_model.invoke(messages)
        return response.content
    
    def retrieve_context(self: Self, question: str) -> List[Document]:
        """ Retrieve proper context from vector store """
        return self.vector_store.db.similarity_search(question)
    
    def build_prompt() -> str:
        system_prompt = """
        Tu es un assistant juridique et fiscal dédié aux propriétaires bailleurs en France.
        Réponds uniquement à partir des éléments du contexte fournis.
        
        Si tu ne sais pas, ne réponds pas. Lorsque tu réponds, indique les numéros, noms
        et dates des lois ou sources utilisées pour assurer la précision et la fiabilité
        des informations fournies.

        Question: {question}
        Context: {context} 
        """

        return PromptTemplate(
            template=system_prompt,
            input_variables=["question", "context"]
        ) 
    
