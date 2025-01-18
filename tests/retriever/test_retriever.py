import unittest

from deepeval.test_case import LLMTestCase
from deepeval import evaluate
from deepeval.metrics import (
    ContextualPrecisionMetric,
    ContextualRecallMetric,
    ContextualRelevancyMetric
)
from deepeval import assert_test

from mevy_bot.vector_store.vector_store import VectorStore
from mevy_bot.vector_store.qdrant_collection import QdrantCollection
from mevy_bot.models.openai import OpenAIModelFactory
from mevy_bot.generator.openai_generator import OpenAIGenerator
from mevy_bot.rewriter.openai_rewriter import OpenAIRewriter


class TestRetriever(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        embedding_model_info = OpenAIModelFactory.text_embedding_3_small()
        generator_model_info = OpenAIModelFactory.gpt4o_mini()

        store_client = QdrantCollection(embedding_model_info.vector_dimensions)
        cls.vector_store = VectorStore(
            store_client, embedding_model_info, generator_model_info)
        cls.collection_name = "mevy-bot-1024_0.2"
        cls.generator = OpenAIGenerator(generator_model_info, cls.vector_store)
        cls.rewriter = OpenAIRewriter(generator_model_info.name)

        # Deepeval metrics
        cls.contextual_precision = ContextualPrecisionMetric(
            model=generator_model_info.name)
        cls.contextual_recall = ContextualRecallMetric(
            model=generator_model_info.name)
        cls.contextual_relevancy = ContextualRelevancyMetric(
            model=generator_model_info.name)

    def test_code_civil(self):

        user_query = "L'Etat a-t-il le droit d'exproprier un propriétaire ?"
        rewrited_query = self.rewriter.rewrite_user_query(user_query)
        retrieved_documents = self.vector_store.search_in_store(
            rewrited_query,
            self.collection_name
        )
        

        retrieved_context = self.generator.list_documents_from_retrieved_context(
            retrieved_documents)

        generated_answer = self.generator.generate_response_with_context(
            rewrited_query, self.collection_name)

        test_case = LLMTestCase(
            input=rewrited_query,
            actual_output=generated_answer,
            expected_output="Oui, l'Etat français peut exproprier un propriétaire dans le cadre d'un \
            projet d'utilité publique moyennant une indemnité juste et préalable (article 545 du Code Civil)",
            retrieval_context=retrieved_context
        )

        assert_test(
            test_case,
            metrics=[self.contextual_precision,
                     self.contextual_recall, self.contextual_relevancy],
        )

    def test_question_hors_contexte(self):
        user_query = "Ecris une fonction Python pour calculer la somme des n premiers entiers"
        rewrited_query = self.rewriter.rewrite_user_query(user_query)
        retrieved_documents = self.vector_store.search_in_store(
            rewrited_query,
            self.collection_name
        )
        retrieved_context = self.generator.list_documents_from_retrieved_context(
            retrieved_documents)

        generated_answer = self.generator.generate_response_with_context(
            rewrited_query, self.collection_name)

        test_case = LLMTestCase(
            input=rewrited_query,
            actual_output=generated_answer,
            expected_output="Désolé, je ne peux pas répondre à cette question. \
                Elle est en dehors de mon domaine de connaissances",
            retrieval_context=retrieved_context
        )

        assert_test(
            test_case,
            metrics=[self.contextual_precision,
                     self.contextual_recall, self.contextual_relevancy],
        )
