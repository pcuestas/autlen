"""Test evaluation of automatas."""
from copy import deepcopy
import os
import unittest
from abc import ABC, abstractmethod
from typing import Optional, Tuple, Type

from automata.utils import write_dot
from automata.automaton import FiniteAutomaton, utils
from automata.automaton_evaluator import FiniteAutomatonEvaluator
from automata.utils import AutomataFormat
from automata.re_parser import REParser


def represent_dot(filename:str,automaton:FiniteAutomaton)->None:
    '''writes dot representation of automata in file 
    with name filename (only file name, not full path)'''
    if any(len(state.name)>30 for state in automaton.states):
        states = deepcopy(automaton.states)
        REParser()._rename_states(states)
        automaton = FiniteAutomaton(states)
    dir_path = os.path.dirname(os.path.realpath(__file__))+'/dot/'
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    with open(dir_path+filename, "w") as f:
        f.write(write_dot(automaton))

class TestDeterministicBase(ABC, unittest.TestCase):
    """
        Base class for string acceptance tests.
    """

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
        represent_dot(type(self).__name__ + 'Original.dot', self.original)
        represent_dot(type(self).__name__ + 'Deterministic.dot',self.automaton)


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
        '''comprueba que el self.automaton es determinista. Es decir,
            todos los estados tienen una (y solo una) transición por cada símbolo
        '''
        alphabet = utils.alphabet(self.original.states)

        # Ver que en cada estado hay al menos una transición para cada símbolo
        self.assertTrue(
            all(# para cada estado
                all(# para cada símbolo
                    any(# existe alguna transición 
                        transition.symbol==symbol
                        for transition in state.transitions 
                    )
                    for symbol in alphabet
                )
                for state in self.automaton.states
            )
        )

        # Ver que de hecho, solo hay exactamente una transición por cada símbolo.
        self.assertTrue(
            all(# para cada estado, hay tantas transiciones como símbolos
                len(alphabet)==len(state.transitions)
                for state in self.automaton.states
            )
        )

    
class TestDeterministic_Hello(TestDeterministicBase):
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


class TestDeterministic_Lambdas(TestDeterministicBase):
    """Acepta solo la cadena vacía. """

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
    

class TestDeterministic_Number(TestDeterministicBase):
    """Acepta números decimales: mismo autómata que en test_evaluator."""

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


class TestDeterministic_WithParser(unittest.TestCase):
    """ 
        Crea un automata a partir de una regex y lo convierte en un determinista.
        Para probar su corrección, se comprueba que es en efecto determinista (_check_deterministic)
        y que sigue aceptando (y rechazando) las mismas cadenas.
    """

    original_evaluator: FiniteAutomatonEvaluator

    def _create_evaluator(
        self, 
        regex: str,
        testname: str
    ) -> Tuple[FiniteAutomatonEvaluator, FiniteAutomaton, FiniteAutomaton]:
        original = REParser().create_automaton(regex)
        deterministic = original.to_deterministic()
        self.original_evaluator = FiniteAutomatonEvaluator(original)

        represent_dot(type(self).__name__ + testname + 'Original.dot', original)
        represent_dot(type(self).__name__ + testname + 'Deterministic.dot', deterministic)

        return FiniteAutomatonEvaluator(deterministic), original, deterministic

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
        evaluator, orig_aut, deter_aut = self._create_evaluator("G.o.o.d.b.y.e", "Goodbye")

        self._check_deterministic(orig_aut,deter_aut)

        self._check_accept(evaluator, "Goodbye", should_accept=True)
        self._check_accept(evaluator, "Gooody", should_accept=False)
        self._check_accept(evaluator, "ByeFD", should_accept=False)
        self._check_accept(evaluator, "oodbye", should_accept=False)
        self._check_accept(evaluator, "Goodbye.", should_accept=False)
        self._check_accept(evaluator, "", should_accept=False)

    def test_star(self) -> None:
        """Test Kleene star."""
        evaluator, orig_aut, deter_aut = self._create_evaluator("a*.b*", "StarConcat")

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
        evaluator, orig_aut, deter_aut = self._create_evaluator("(a+b)*.c", "OrStar")

        self._check_deterministic(orig_aut, deter_aut)

        self._check_accept(evaluator, "c", should_accept=True)
        self._check_accept(evaluator, "ac", should_accept=True)
        self._check_accept(evaluator, "bc", should_accept=True)
        self._check_accept(evaluator, "aac", should_accept=True)
        self._check_accept(evaluator, "bbc", should_accept=True)
        self._check_accept(evaluator, "abc", should_accept=True)
        self._check_accept(evaluator, "bac", should_accept=True)
        self._check_accept(evaluator, "aabc", should_accept=True)
        self._check_accept(evaluator, "abbc", should_accept=True)
        self._check_accept(evaluator, "abac", should_accept=True)
        self._check_accept(evaluator, "babc", should_accept=True)
        self._check_accept(evaluator, "", should_accept=False)
        self._check_accept(evaluator, "ab", should_accept=False)
        self._check_accept(evaluator, "ba", should_accept=False)
        self._check_accept(evaluator, "aab", should_accept=False)
        self._check_accept(evaluator, "abb", should_accept=False)
        self._check_accept(evaluator, "aba", should_accept=False)
        self._check_accept(evaluator, "bab", should_accept=False)
        self._check_accept(evaluator, "cc", should_accept=False)
        self._check_accept(evaluator, "acbc", should_accept=False)
        self._check_accept(evaluator, "bca", should_accept=False)
        self._check_accept(evaluator, "aabcc", should_accept=False)
        self._check_accept(evaluator, "cabb", should_accept=False)
        self._check_accept(evaluator, "abca", should_accept=False)
        self._check_accept(evaluator, "babcccc", should_accept=False)

    def test_number(self) -> None:
        """Test decimal numbers that follow the format of the previous practice"""
        num = "(0+1+2+3+4+5+6+7+8+9)"
        evaluator, orig_aut, deter_aut = self._create_evaluator(
            f"({num}.{num}*.,.{num}*)+{num}*",
            "NumberExpression"
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
            all(# para cada estado
                all(# para cada símbolo
                    any(# existe alguna transición 
                        transition.symbol==symbol
                        for transition in state.transitions 
                    )
                    for symbol in alphabet
                )
                for state in deterministic.states
            )
        )
        self.assertTrue(
            all(# para cada estado, hay tantas transiciones como símbolos
                len(alphabet)==len(state.transitions)
                for state in deterministic.states
            )
        )

if __name__ == '__main__':
    unittest.main()
