from typing import Self
from abc import ABC, abstractmethod


class Classifier(ABC):

    @abstractmethod
    def classify_user_query(self: Self, user_query: str) -> str:
        pass
