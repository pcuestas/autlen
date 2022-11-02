"""Test evaluation of automatas."""
from typing import List, Tuple
import unittest
from abc import ABC, abstractmethod

from automata.automaton import FiniteAutomaton, State
from automata.automaton_evaluator import FiniteAutomatonEvaluator
from automata.re_parser import REParser
from automata.tests.our_test_to_deterministic import represent_dot


class TestMinimizedBase(ABC, unittest.TestCase):
    """Tests for to_deterministic method."""

    original_evaluator: FiniteAutomatonEvaluator
    minimized_evaluator: FiniteAutomatonEvaluator
    original: FiniteAutomaton
    minimized: FiniteAutomaton
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
    ) -> Tuple[FiniteAutomatonEvaluator, FiniteAutomatonEvaluator, FiniteAutomaton]:
        self.original = REParser().create_automaton(self.regex)
        det = self.original.to_deterministic()
        det.states.append(State("extra", True))
        det.states.append(State("extra2", True))
        self.minimized = det.to_minimized()
        self.original_evaluator = FiniteAutomatonEvaluator(self.original)
        self.minimized_evaluator = FiniteAutomatonEvaluator(self.minimized)

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

    def _test_string(self) -> None:
        """Test fixed regex."""
        self.assertEqual(len(self.minimized.states), self.min_states_number)

        for test_string in self.test_strings:
            self._check_same(test_string)

# comienzan los casos de test:

class TestMinimized_Hello(TestMinimizedBase):
    def _regex(self) -> str:
        return "H.e.l.l.o"
    def _min_states_num(self) -> int:
        return 7
    def _test_strings(self) -> List[str]:
        return ["Hello", "Hella", "hello", "", "Hiello"]

    def test_string(self)->None:
        self._test_string()

class TestMinimized_ABC(TestMinimizedBase):
    def _regex(self) -> str:
        return "a.b*.(a+c.b)*"
    def _min_states_num(self) -> int:
        return 5
    def _test_strings(self) -> List[str]:
        return ["abbb", "abcba", "aaacb", "", "acb", "bbb","aab","aba"]

    def test_string(self)->None:
        self._test_string()

class TestMinimized_AB(TestMinimizedBase):
    def _regex(self) -> str:
        return "(a+b)*"
    def _min_states_num(self) -> int:
        return 1
    def _test_strings(self) -> List[str]:
        return ["abbb", "abba", "aaab", "", "ab", "bbab","aab","aba"]

    def test_string(self)->None:
        self._test_string()

class TestMinimized_BAislada(TestMinimizedBase):
    def _regex(self) -> str:
        return "(λ+b).(a+a.b)*"
    def _min_states_num(self) -> int:
        return 3
    def _test_strings(self) -> List[str]:
        return ["babaaababaa", "babba", "abababb", "", "bab", "babab","abbab","bbaba"]

    def test_string(self)->None:
        self._test_string()

class TestMinimized_BPares1(TestMinimizedBase):
    def _regex(self) -> str:
        return "(a*.b.a*.b.a*)*"
    def _min_states_num(self) -> int:
        return 2
    def _test_strings(self) -> List[str]:
        return ["babaaababaa", "babba", "abababb", "", "bab", "babab","abbab","bbaba"]

    def test_string(self)->None:
        self._test_string()

class TestMinimized_BPares2(TestMinimizedBase):
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
