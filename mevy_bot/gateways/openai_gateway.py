import logging
from typing import Self, Generator

from openai import OpenAI

from mevy_bot.exceptions.no_response_error import NoResponseError

logger = logging.getLogger()


class OpenAIGateway:

    MODEL_TEMPERATURE = 0

    def __init__(self: Self, model_name: str) -> None:
        self.openai_client = OpenAI()
        self.model_name = model_name

    def send_query(
            self: Self,
            system_prompt: str,
            user_prompt: str, ) -> str:

        completion = self.openai_client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            stream=False
        )

        model_response = completion.choices[0].message.content

        if model_response is None:
            raise NoResponseError()

        return model_response

    def send_query_stream(
        self: Self,
        system_prompt: str,
        user_prompt: str
    ) -> Generator:
        response = self.openai_client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            stream=True
        )

        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
