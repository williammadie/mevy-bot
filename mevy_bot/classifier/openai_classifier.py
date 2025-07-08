from typing import Self
from mevy_bot.classifier.classifier import Classifier
from mevy_bot.gateways.openai_gateway import OpenAIGateway


class OpenAIClassifier(Classifier):

    def __init__(self: Self, model_name: str) -> None:
        self.openai_gateway = OpenAIGateway(model_name)

    def classify_user_query(self: Self, user_query: str) -> str:
        system_prompt = self.build_classifier_prompt()
        return self.openai_gateway.send_query(
            system_prompt=system_prompt,
            user_prompt=user_query
        )

    def build_classifier_prompt(self: Self) -> str:
        return """
        Classifie la question suivante dans l'une des catégories suivantes (réponds uniquement par le nom de la catégorie) :

        - juridique : question juridique ou fiscale d’un propriétaire bailleur en France
        - meta : question sur ce que tu sais faire, ton fonctionnement ou ton rôle
        - social : salutation, remerciement ou politesse
        - hors sujet : tout le reste
        """
