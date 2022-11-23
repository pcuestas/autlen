import unittest
from typing import AbstractSet

from src.grammar import Grammar
from src.utils import GrammarFormat


class TestFirst(unittest.TestCase):
    def _check_first(
        self,
        grammar: Grammar,
        input_string: str,
        first_set: AbstractSet[str],
    ) -> None:
        with self.subTest(
            string=f"First({input_string}), expected {first_set}",
        ):
            computed_first = grammar.compute_first(input_string)
            self.assertEqual(computed_first, first_set)

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
        self._check_first(grammar, "E", {'(', 'i'})
        self._check_first(grammar, "T", {'(', 'i'})
        self._check_first(grammar, "X", {'', '+'})
        self._check_first(grammar, "Y", {'', '*'})
        self._check_first(grammar, "", {''})
        self._check_first(grammar, "Y+i", {'+', '*'})
        self._check_first(grammar, "YX", {'+', '*', ''})
        self._check_first(grammar, "YXT", {'+', '*', 'i', '('})

    def test_case2(self) -> None:
        """Test Case 2."""
        grammar_str = """
        E -> X
        X -> Y
        Y -> E
        Y -> i
        """

        grammar = GrammarFormat.read(grammar_str)
        self._check_first(grammar, "E", {'i'})
        self._check_first(grammar, "X", {'i'})
        self._check_first(grammar, "Y", {'i'})
        self._check_first(grammar, "i", {'i'})


if __name__ == '__main__':
    unittest.main()
