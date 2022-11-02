"""Test evaluation of automatas."""
from random import random
from typing import List, Tuple
import unittest
from abc import ABC, abstractmethod

from automata.automaton import FiniteAutomaton, State
from automata.automaton_evaluator import FiniteAutomatonEvaluator
from automata.re_parser import REParser
from automata.tests.our_test_to_deterministic import represent_dot


class TestMinimizedBase(ABC, unittest.TestCase):
    """ 
        Estos test prueban el proceso de minimización de un automata. Para ello
        se realiza los siguiente:

        1. A partir de una regex se genera un autómata finito (usando las funciones en re_parser.py
        y automaton.py)

        2. Se añaden varios estados inaccesibles

        3. Se comprueba que la versión minimizada acepta las mismas cadenas (corrección) y que tiene el número
        de estados mínimos (minimización)
    """

    original_evaluator: FiniteAutomatonEvaluator
    minimized_evaluator: FiniteAutomatonEvaluator
    minimized_evaluator2: FiniteAutomatonEvaluator
    original: FiniteAutomaton
    minimized: FiniteAutomaton
    minimized2: FiniteAutomaton
    regex: str
    min_states_number: int
    test_strings: List[str]

    @abstractmethod
    def _regex(self)->str:
        pass
    @abstractmethod
    def _min_states_num(self)->int:
        pass
    @abstractmethod
    def _test_strings(self)->List[str]:
        pass

    def setUp(self) -> None:
        self.regex = self._regex()
        self.min_states_number = self._min_states_num()
        self.test_strings = self._test_strings()
        self._create_evals_minimized()

    def _create_evals_minimized(
        self
    ) -> None:
        self.original = REParser().create_automaton(self.regex)
        det = self.original.to_deterministic()
        if random()<.3: det.states.append(State("extra", True))
        if random()<.3: det.states.append(State("extra2", True))
        self.minimized = self.original.to_minimized()
        self.minimized2 = det.to_minimized()
        self.original_evaluator = FiniteAutomatonEvaluator(self.original)
        self.minimized_evaluator = FiniteAutomatonEvaluator(self.minimized)
        self.minimized_evaluator2 = FiniteAutomatonEvaluator(self.minimized2)

        represent_dot(type(self).__name__ + 'OriginalDet.dot', det)
        represent_dot(type(self).__name__ + 'Minimized.dot',self.minimized)

    def _check_same(
        self,
        string: str
    ) -> None:
        with self.subTest(string=string):
            self.assertEqual(
                self.original_evaluator.accepts(string),
                self.minimized_evaluator.accepts(string)
            )
            self.assertEqual(
                self.original_evaluator.accepts(string),
                self.minimized_evaluator2.accepts(string)
            )

    def _test_string(self) -> None:
        """
            Comprobar que tiene el mínimo número de estados y que acepta las mismas cadenas
        """
        self.assertEqual(len(self.minimized.states), self.min_states_number)
        self.assertEqual(len(self.minimized2.states), self.min_states_number)

        for test_string in self.test_strings:
            self._check_same(test_string)

# comienzan los casos de test:

class TestMinimized_Hello(TestMinimizedBase):
    """Testeamos un autómata que acepta una solamente una cadena: 'Hello'"""
    def _regex(self) -> str:
        return "H.e.l.l.o"
    def _min_states_num(self) -> int:
        return 7
    def _test_strings(self) -> List[str]:
        return ["Hello", "Hella", "hello", "", "Hiello"]

    def test_string(self)->None:
        self._test_string()

class TestMinimized_ABC(TestMinimizedBase):
    """Testea un autómata con regex "a.b*.(a+c.b)*" """
    def _regex(self) -> str:
        return "a.b*.(a+c.b)*"
    def _min_states_num(self) -> int:
        return 5
    def _test_strings(self) -> List[str]:
        return ["abbb", "abcba", "aaacb", "", "acb", "bbb","aab","aba"]

    def test_string(self)->None:
        self._test_string()

class TestMinimized_AB(TestMinimizedBase):
    """Este autómata acepta cualquier cadena de a's y b's"""
    def _regex(self) -> str:
        return "(a+b)*"
    def _min_states_num(self) -> int:
        return 1
    def _test_strings(self) -> List[str]:
        return ["abbb", "abba", "aaab", "", "ab", "bbab","aab","aba", "abas"]

    def test_string(self)->None:
        self._test_string()

class TestMinimized_BAislada(TestMinimizedBase):
    """Este autómata acepta cualquier cadena de a's y b's
        que no contenga dos b's seguidas"""
    def _regex(self) -> str:
        return "(λ+b).(a+a.b)*"
    def _min_states_num(self) -> int:
        return 3
    def _test_strings(self) -> List[str]:
        return ["babaaababaa", "babba", "abababb", "", "bab", "babab","abbab","bbaba"]

    def test_string(self)->None:
        self._test_string()

class TestMinimized_BPares1(TestMinimizedBase):
    """Este autómata acepta cadenas de a's y b's con 
    número par de b's"""
    def _regex(self) -> str:
        return "(a*.b.a*.b.a*)*"
    def _min_states_num(self) -> int:
        return 2
    def _test_strings(self) -> List[str]:
        return ["babaaababaa", "babba", "abababb", "", "bab", "babab","abbab","bbaba"]

    def test_string(self)->None:
        self._test_string()

class TestMinimized_BPares2(TestMinimizedBase):
    """Este autómata acepta cadenas de a's y b's con 
    número par de b's. Observación: acepta las mismas cadenas
    que el anterior. Sin embargo, el autómata original es 
    muy diferente mientras que el minimizado es el mismo"""
    def _regex(self) -> str:
        return "(a+b.a*.b)*"
    def _min_states_num(self) -> int:
        return 2
    def _test_strings(self) -> List[str]:
        return ["babaaababaa", "babba", "abababb", "", "bab", "babab","abbab","bbaba"]

    def test_string(self)->None:
        self._test_string()


if __name__ == '__main__':
    unittest.main()
