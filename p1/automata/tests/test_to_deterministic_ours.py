"""Test evaluation of automatas."""
import unittest
from abc import ABC, abstractmethod
from typing import Optional, Tuple, Type

from automata.automaton import FiniteAutomaton, utils
from automata.automaton_evaluator import FiniteAutomatonEvaluator
from automata.utils import AutomataFormat
from automata.re_parser import REParser


class TestEvaluatorBase(ABC, unittest.TestCase):
    """Base class for string acceptance tests."""

    automaton: FiniteAutomaton
    original: FiniteAutomaton
    evaluator: FiniteAutomatonEvaluator

    @abstractmethod
    def _create_automata(self) -> FiniteAutomaton:
        pass

    def setUp(self) -> None:
        """Set up the tests."""
        self.original = self._create_automata()
        self.automaton = self.original.to_deterministic()
        self.original_evaluator = FiniteAutomatonEvaluator(self.original)
        self.evaluator = FiniteAutomatonEvaluator(self.automaton)

    def _check_accept_body(
        self,
        string: str,
        should_accept: bool = True,
    ) -> None:
        accepted = self.evaluator.accepts(string)
        truth = self.original_evaluator.accepts(string)
        self.assertEqual(accepted, should_accept)
        self.assertEqual(accepted, truth)

    def _check_accept(
        self,
        string: str,
        should_accept: bool = True,
        exception: Optional[Type[Exception]] = None,
    ) -> None:

        with self.subTest(string=string):
            if exception is None:
                self._check_accept_body(string, should_accept)
            else:
                with self.assertRaises(exception):
                    self._check_accept_body(string, should_accept)
    
    def _check_deterministic(self) -> None:
        alphabet = utils.alphabet(self.original.states)
        self.assertTrue(
            all(
                all(
                    any(
                        transition.symbol==symbol
                        for transition in state.transitions 
                    )
                    for symbol in alphabet
                )
                for state in self.automaton.states
            )
        )

    
class TestEvaluatorFixed(TestEvaluatorBase):
    """Test for a fixed string."""

    def _create_automata(self) -> FiniteAutomaton:

        description = """
        Automaton:

            Empty
            H
            He
            Hel
            Hell
            Hello final

            Empty -H-> H
            H -e-> He
            He -l-> Hel
            Hel -l-> Hell
            Hell -o-> Hello
        """

        return AutomataFormat.read(description)

    def test_fixed(self) -> None:
        """Test for a fixed string."""
        self._check_deterministic()
        self._check_accept("Hello", should_accept=True)
        self._check_accept("Helloo", should_accept=False)
        self._check_accept("Hell", should_accept=False)
        self._check_accept("llH", should_accept=False)
        self._check_accept("", should_accept=False)
        self._check_accept("Hella", should_accept=False)
        self._check_accept("aHello", should_accept=False)
        self._check_accept("Helloa", should_accept=False)


class TestEvaluatorLambdas(TestEvaluatorBase):
    """Test for a fixed string."""

    def _create_automata(self) -> FiniteAutomaton:

        description = """
        Automaton:

            1
            2
            3
            4 final

            1 --> 2
            2 --> 3
            3 --> 4
        """

        return AutomataFormat.read(description)

    def test_lambda(self) -> None:
        """Test for a fixed string."""
        self._check_deterministic()
        self._check_accept("", should_accept=True)
        self._check_accept("a", should_accept=False)
    

class TestEvaluatorNumber(TestEvaluatorBase):
    """Test for a fixed string."""

    def _create_automata(self) -> FiniteAutomaton:

        description = """
        Automaton:

            initial
            sign
            int final
            dot
            decimal final

            initial ---> sign
            initial --> sign
            sign -0-> int
            sign -1-> int
            int -0-> int
            int -1-> int
            int -.-> dot
            dot -0-> decimal
            dot -1-> decimal
            decimal -0-> decimal
            decimal -1-> decimal
        """

        return AutomataFormat.read(description)

    def test_number(self) -> None:
        """Test for a fixed string."""
        self._check_accept("0", should_accept=True)
        self._check_accept("0.0", should_accept=True)
        self._check_accept("0.1", should_accept=True)
        self._check_accept("1.0", should_accept=True)
        self._check_accept("-0", should_accept=True)
        self._check_accept("-0.0", should_accept=True)
        self._check_accept("-0.1", should_accept=True)
        self._check_accept("-1.0", should_accept=True)
        self._check_accept("-101.010", should_accept=True)
        self._check_accept("0.", should_accept=False)
        self._check_accept(".0", should_accept=False)
        self._check_accept("0.0.0", should_accept=False)
        self._check_accept("0-0.0", should_accept=False)


class TestREParser(unittest.TestCase):
    """Tests for to_deterministic method."""

    original_evaluator: FiniteAutomatonEvaluator

    def _create_evaluator(
        self, 
        regex: str
    ) -> Tuple[FiniteAutomatonEvaluator, FiniteAutomaton, FiniteAutomaton]:
        original = REParser().create_automaton(regex)
        automaton = original.to_deterministic()
        self.original_evaluator = FiniteAutomatonEvaluator(original)
        return FiniteAutomatonEvaluator(automaton), original, automaton

    def _check_accept(
        self,
        evaluator: FiniteAutomatonEvaluator,
        string: str,
        should_accept: bool = True,
    ) -> None:
        with self.subTest(string=string):
            accepted = evaluator.accepts(string)
            truth = self.original_evaluator.accepts(string)
            self.assertEqual(accepted, should_accept)
            self.assertEqual(accepted, truth)

    def test_fixed(self) -> None:
        """Test fixed regex."""
        evaluator, orig_aut, deter_aut = self._create_evaluator("H.e.l.l.o")

        self._check_deterministic(orig_aut,deter_aut)

        self._check_accept(evaluator, "Hello", should_accept=True)
        self._check_accept(evaluator, "Helloo", should_accept=False)
        self._check_accept(evaluator, "Hell", should_accept=False)
        self._check_accept(evaluator, "llH", should_accept=False)
        self._check_accept(evaluator, "", should_accept=False)

    def test_star(self) -> None:
        """Test Kleene star."""
        evaluator, orig_aut, deter_aut = self._create_evaluator("a*.b*")

        self._check_deterministic(orig_aut, deter_aut)
        
        self._check_accept(evaluator, "", should_accept=True)
        self._check_accept(evaluator, "a", should_accept=True)
        self._check_accept(evaluator, "b", should_accept=True)
        self._check_accept(evaluator, "aa", should_accept=True)
        self._check_accept(evaluator, "bb", should_accept=True)
        self._check_accept(evaluator, "ab", should_accept=True)
        self._check_accept(evaluator, "ba", should_accept=False)
        self._check_accept(evaluator, "aab", should_accept=True)
        self._check_accept(evaluator, "abb", should_accept=True)
        self._check_accept(evaluator, "aba", should_accept=False)
        self._check_accept(evaluator, "bab", should_accept=False)

    def test_or(self) -> None:
        """Test Kleene star."""
        evaluator, orig_aut, deter_aut = self._create_evaluator("(a+b)*")

        self._check_deterministic(orig_aut, deter_aut)

        self._check_accept(evaluator, "", should_accept=True)
        self._check_accept(evaluator, "a", should_accept=True)
        self._check_accept(evaluator, "b", should_accept=True)
        self._check_accept(evaluator, "aa", should_accept=True)
        self._check_accept(evaluator, "bb", should_accept=True)
        self._check_accept(evaluator, "ab", should_accept=True)
        self._check_accept(evaluator, "ba", should_accept=True)
        self._check_accept(evaluator, "aab", should_accept=True)
        self._check_accept(evaluator, "abb", should_accept=True)
        self._check_accept(evaluator, "aba", should_accept=True)
        self._check_accept(evaluator, "bab", should_accept=True)

    def test_number(self) -> None:
        """Test number expression."""
        num = "(0+1+2+3+4+5+6+7+8+9)"
        evaluator, orig_aut, deter_aut = self._create_evaluator(
            f"({num}.{num}*.,.{num}*)+{num}*",
        )
        self._check_deterministic(orig_aut, deter_aut)

        self._check_accept(evaluator, ",", should_accept=False)
        self._check_accept(evaluator, "1,7", should_accept=True)
        self._check_accept(evaluator, "25,73", should_accept=True)
        self._check_accept(evaluator, "5027", should_accept=True)
        self._check_accept(evaluator, ",13", should_accept=False)
        self._check_accept(evaluator, "13,", should_accept=True)
        self._check_accept(evaluator, "3,7,12", should_accept=False)

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
