"""Test evaluation of automatas."""
from typing import Tuple
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

    def test_1(self) -> None:
        """Test fixed regex."""
        evaluator_original, evaluator_minimized, automaton_minimized = self._create_evals_minimized("H.e.l.l.o")
        
        self.assertEqual(len(automaton_minimized.states), 7)

        self._check_same(evaluator_original, evaluator_minimized, "Hello")
        self._check_same(evaluator_original, evaluator_minimized, "Hella")
        self._check_same(evaluator_original, evaluator_minimized, "Helio")
        self._check_same(evaluator_original, evaluator_minimized, "Hel-o")
        self._check_same(evaluator_original, evaluator_minimized, "hello")
        self._check_same(evaluator_original, evaluator_minimized, "ello")
        self._check_same(evaluator_original, evaluator_minimized, "Helllo")

    def _check_deterministic(
        self, 
        original: FiniteAutomaton,
        deterministic: FiniteAutomaton
    ) -> None:
        alphabet = utils.alphabet(original.states)
        self.assertTrue(
            all(
                all(
                    any(
                        transition.symbol==symbol
                        for transition in state.transitions 
                    )
                    for symbol in alphabet
                )
                for state in deterministic.states
            )
        )



if __name__ == '__main__':
    unittest.main()
