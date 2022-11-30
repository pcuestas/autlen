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
        self._check_first(grammar, "", {''})

    def test_new1(self) -> None:
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
        self._check_first(grammar, "A", {'1', '0', 'e', ',', '.'})
        self._check_first(grammar, "B", {'', '1', '0'})
        self._check_first(grammar, "X", {'e', ',', '.'})
        self._check_first(grammar, "XB", {'e', ',', '.'})
        self._check_first(grammar, "BX", {'1', '0', 'e', ',', '.'})
        self._check_first(grammar, ".XB", {'.'})
        self._check_first(grammar, "BBBBB", {'', '1', '0'})
        self._check_first(grammar, "BBBBB.", {'.', '1', '0'})
        self._check_first(grammar, "", {''})


    def test_new2(self) -> None:
        """Ej. 2. Hoja LL1"""
        grammar_str = """
        A -> BCD
        B -> <
        B ->
        C -> 0C;
        C -> 1C;
        D -> 0>
        D -> 1>
        """

        grammar = GrammarFormat.read(grammar_str)
        self._check_first(grammar, "A", {'1', '0', '<'})
        self._check_first(grammar, "B", {'','<'})
        self._check_first(grammar, "C", {'1', '0'})
        self._check_first(grammar, "D", {'1', '0',})
        self._check_first(grammar, "BA", {'1', '0', '<'})
        self._check_first(grammar, "0AB", {'0'})
       

if __name__ == '__main__':
    unittest.main()
