from typing import Self

from mevy_bot.query_handler.query_handler import QueryHandler
from mevy_bot.models.openai import ChatModel


class OpenAIQueryHandler(QueryHandler):

    def __init__(self: Self, chat_model: ChatModel) -> None:
        self.chat_model = chat_model

    def generate_response_with_context(self: Self, question: str, collection_name: str) -> str:
        context_documents = self.retrieve_context_documents(
            question, collection_name)

        context = ""
        for doc in context_documents:
            if doc.payload is not None:
                doc_content = doc.payload.get('text')
                context += f'{doc_content}\n\n'

        system_prompt = self.build_system_prompt()
        user_prompt = self.build_user_prompt(question, context)

        completion = self.llm_model.chat.completions.create(
            model=self.chat_model.name,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            temperature=self.MODEL_TEMPERATURE
        )

        return completion
