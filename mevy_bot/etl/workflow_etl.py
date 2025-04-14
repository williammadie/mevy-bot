from typing import Self
from abc import ABC, abstractmethod

from mevy_bot.models.openai import OpenAIModelFactory
from mevy_bot.etl.workflow_logger import WorkflowLogger


class WorkflowEtl(ABC):

    def __init__(self: Self, workflow_logger: WorkflowLogger) -> None:
        self.logger = workflow_logger
        self.embedding_model_info = OpenAIModelFactory.text_embedding_3_small()
        self.generator_model_info = OpenAIModelFactory.gpt4o_mini()
        self.collection_name = "mevy_bot"

    @abstractmethod
    def run(self: Self, predict_only: bool = False) -> None:
        self.logger.info(f"Starting workflow {self.__class__.__name__}")
    
    def get_workflow_logger(self: Self) -> WorkflowLogger:
        return self.logger
