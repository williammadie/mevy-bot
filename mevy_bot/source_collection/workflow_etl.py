import logging
from typing import Self
from abc import ABC, abstractmethod


logger = logging.getLogger()


class WorkflowEtl(ABC):

    @abstractmethod
    def run(self: Self, predict_only: bool = False) -> None:
        logger.info("Starting workflow %s", self.__class__.__name__)
