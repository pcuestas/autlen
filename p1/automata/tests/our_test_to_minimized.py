"""Test evaluation of automatas."""
from typing import List, Tuple
import unittest
from abc import ABC

from automata.automaton import FiniteAutomaton, utils
from automata.automaton_evaluator import FiniteAutomatonEvaluator
from re_parser import REParser



class TestREParser(unittest.TestCase):
    """Tests for to_deterministic method."""

    def _create_evals_minimized(
        self, 
        regex: str
    ) -> Tuple[FiniteAutomatonEvaluator, FiniteAutomatonEvaluator, FiniteAutomaton]:
        original = REParser().create_automaton(regex)
        minimized = original.to_minimized()
        return FiniteAutomatonEvaluator(original), FiniteAutomatonEvaluator(minimized), minimized

    def _check_same(
        self,
        eval1: FiniteAutomatonEvaluator,
        eval2: FiniteAutomatonEvaluator,
        string: str,
    ) -> None:
        with self.subTest(string=string):
            self.assertEqual(
                eval1.accepts(string),
                eval2.accepts(string)
            )

    def _test_string(self, string:str, min_states_number:int, test_strings:List[str]) -> None:
        """Test fixed regex."""
        evaluator_original, evaluator_minimized, automaton_minimized = self._create_evals_minimized(string)

        self.assertEqual(len(automaton_minimized.states), min_states_number)

        for test_string in test_strings:
            self._check_same(evaluator_original, evaluator_minimized, test_string)

    def test_all(self):
        tests: List[Tuple[str, int, List[str]]] = [
            ("H.e.l.l.o", 7, ["Hello", "Hella", "hello", "", "Hiello"])
        ]

        for test in tests:
            self._test_string(test[0], test[1], test[2])



if __name__ == '__main__':
    unittest.main()
