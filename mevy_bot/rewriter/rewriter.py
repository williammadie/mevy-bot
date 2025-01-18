from typing import Self
from abc import ABC, abstractmethod

from mevy_bot.models.openai import ChatModel
from mevy_bot.gateways.openai_gateway import OpenAIGateway


class Rewriter(ABC):

    @abstractmethod
    def rewrite_user_query(self: Self, user_query: str) -> str:
        pass

    def build_rewriter_prompt(self: Self) -> str:
        return """
        Vous êtes un assistant utile qui génère plusieurs requêtes de recherche
        à partir d'une seule requête d'entrée.

        Le contexte de la requête portera toujours sur les locataires et les
        propriétaires en France.

        Effectuez une expansion de requête. S'il existe plusieurs façons courantes
        de formuler une question d'utilisateur ou des synonymes courants pour des
        mots-clés dans la question, assurez-vous de retourner plusieurs versions
        de la requête avec des formulations différentes.

        S'il y a des acronymes ou des mots que vous ne connaissez pas,
        ne tentez pas de les reformuler.

        Retournez 3 versions différentes de la question.
        """
