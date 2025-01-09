import unittest
from decimal import Decimal

from mevy_bot.embedder.cost_predictor import CostPredictor


class TestCostPredictor(unittest.TestCase):

    def test_calculate_embedding_cost_ada_v2(self):
        actual_embedding_cost = CostPredictor.calculate_embedding_cost(
            6210,
            1000,
            Decimal('0.0001')
        )
        actual_rounded_embedding_cost = Decimal(round(actual_embedding_cost, 5))
        expected_embedding_cost = Decimal('0.15525')
        self.assertEqual(
            actual_rounded_embedding_cost.compare(expected_embedding_cost),
            Decimal('0')
        )

    def test_calculate_embedding_cost_from_tokens_ada_v2(self):
        actual_embedding_cost = CostPredictor.calculate_embedding_cost_from_tokens(
            Decimal(19_783_176),
            Decimal('0.0001')
        )
        actual_rounded_embedding_cost = Decimal(
            round(actual_embedding_cost, 2))
        expected_embedding_cost = Decimal('1.98')
        self.assertEqual(
            actual_rounded_embedding_cost.compare(expected_embedding_cost),
            Decimal('0')
        )
