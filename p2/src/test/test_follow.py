import unittest
from typing import AbstractSet

from src.grammar import Grammar
from src.utils import GrammarFormat


class TestFollow(unittest.TestCase):
    def _check_follow(
        self,
        grammar: Grammar,
        symbol: str,
        follow_set: AbstractSet[str],
    ) -> None:
        with self.subTest(string=f"Follow({symbol}), expected {follow_set}"):
            computed_follow = grammar.compute_follow(symbol)
            self.assertEqual(computed_follow, follow_set)

    def test_case1(self) -> None:
        """Test Case 1."""
        grammar_str = """
        E -> TX
        X -> +E
        X ->
        T -> iY
        T -> (E)
        Y -> *T
        Y ->
        """

        grammar = GrammarFormat.read(grammar_str)
        self._check_follow(grammar, "E", {'$', ')'})
        self._check_follow(grammar, "T", {'$', ')', '+'})
        self._check_follow(grammar, "X", {'$', ')'})
        self._check_follow(grammar, "Y", {'$', ')', '+'})

    def test_case2(self) -> None:
        """Ej. 1 de primero y siguiente. Hoja LR0/SLR1"""
        grammar_str = """
        A -> BXB
        X -> ,
        X -> .
        X -> e
        B -> 0B
        B -> 1B
        B -> 
        """
        grammar = GrammarFormat.read(grammar_str)
        self._check_follow(grammar, "A", {'$'})
        self._check_follow(grammar, "B", {'$', 'e', '.', ','})
        self._check_follow(grammar, "X", {'$', '1', '0'})

if __name__ == '__main__':
    unittest.main()
