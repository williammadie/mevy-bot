from typing import Self

from mevy_bot.query_handler.query_handler import QueryHandler

class OpenAIQueryHandler(QueryHandler):

    def generate_response(self: Self, question: str) -> str:
        context_documents = self.retrieve_context_documents(question)
        context = "\n\n".join(
            doc.page_content for doc in context_documents)

        system_prompt = self.build_system_prompt()
        user_prompt = self.build_user_prompt(question, context)

        completion = self.llm_model.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": user_prompt
                }
            ]
        )

        return completion
