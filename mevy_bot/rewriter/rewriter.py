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
        Vous êtes un assistant qui reformule une requête utilisateur pour en améliorer la précision et la clarté, sans y répondre.

        Votre tâche est de produire une **version enrichie de la requête d’origine**, en ajoutant les éléments implicites utiles, en précisant les termes flous ou ambigus, et en utilisant des synonymes ou formulations courantes, **sans changer l’intention de l’utilisateur**.

        Le sujet porte toujours sur les relations entre **locataires et propriétaires en France** : droits, obligations, contrats, litiges, etc.

        Contraintes :
        - N’émettez **aucune réponse** à la place du chatbot.
        - Ne posez **pas de nouvelles questions**.
        - Ne vous exprimez **pas à la première ou deuxième personne**.
        - Ne changez **pas le sens** de la question.
        - Ne reformulez **pas** les acronymes ou termes inconnus.
        - Si la requête est trop vague, **précisez seulement dans le contexte du sujet** (par exemple, droits des locataires, impayés, etc.)

        Exemples :
        - Entrée : "Comment peux-tu m'aider ?"
        Sortie : "Quels types d'aide sont disponibles pour un locataire ou un propriétaire en France, notamment en matière de droits, obligations ou conflits locatifs ?"

        - Entrée : "APL pour un étudiant"
        Sortie : "Quelles sont les conditions d’éligibilité à l’APL pour un étudiant locataire en France ?"
        """
