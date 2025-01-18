from typing import Self
from mevy_bot.rewriter.rewriter import Rewriter
from mevy_bot.gateways.openai_gateway import OpenAIGateway


class OpenAIRewriter(Rewriter):

    def __init__(self: Self, model_name: str) -> None:
        self.openai_gateway = OpenAIGateway(model_name)

    def rewrite_user_query(self: Self, user_query: str) -> str:
        system_prompt = self.build_rewriter_prompt()
        return self.openai_gateway.send_query(
            system_prompt=system_prompt,
            user_prompt=user_query
        )
