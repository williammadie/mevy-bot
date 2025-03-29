import logging
from typing import Self
from abc import ABC, abstractmethod

from mevy_bot.models.openai import OpenAIModelFactory

logger = logging.getLogger()


class WorkflowEtl(ABC):

    def __init__(self: Self) -> None:
        self.embedding_model_info = OpenAIModelFactory.text_embedding_3_small()
        self.generator_model_info = OpenAIModelFactory.gpt4o_mini()
        self.collection_name = "mevy_bot"

    @abstractmethod
    def run(self: Self, predict_only: bool = False) -> None:
        logger.info("Starting workflow %s", self.__class__.__name__)
