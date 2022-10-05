"""General utilities to work with automatas."""
import re
from collections import defaultdict, deque
from typing_extensions import Final
from automata.automaton import FiniteAutomaton, Transition, State

import automata.automaton as aut

from typing import (
    DefaultDict,
    Dict,
    Mapping,
    Optional,
    Set,
    List,
)

class FormatParseError(Exception):
    """Exception for parsing problems."""


class AutomataFormat():
    """Custom format to write and read automata."""

    re_comment: Final = re.compile(r"\s*#\.*")
    re_empty: Final = re.compile(r"\s*")
    re_automaton: Final = re.compile(r"\s*Automaton:\s*")
    re_state: Final = re.compile(r"\s*(\w+)(?:\s*(final))?\s*")
    re_transition: Final = re.compile(r"\s*(\w+)\s*-(\S)?->\s*(\w+)\s*")

    @classmethod
    def read(cls, description: str) -> aut.FiniteAutomaton:
        """Read the automaton description in our custom format."""
        splitted_lines = description.splitlines()
        prelude_read = False

        states: Dict[str, aut.State] = {}
        transitions: Set[aut.Transition] = set()

        for line in splitted_lines:
            if cls.re_comment.fullmatch(line) or cls.re_empty.fullmatch(line):
                continue

            if prelude_read:
                match = cls.re_state.fullmatch(line)
                if match:
                    state_name, final_text = match.groups()
                    states[state_name] = aut.State(
                        name=state_name,
                        is_final=bool(final_text),
                    )
                    continue

                match = cls.re_transition.fullmatch(line)
                if match:
                    state1_name, symbol, state2_name = match.groups()
                    states[state1_name].add_transitions([aut.Transition(symbol, state2_name)])
                    continue

            elif cls.re_automaton.fullmatch(line):
                prelude_read = True
                continue

            raise FormatParseError(f"Invalid line: {line}")

        return aut.FiniteAutomaton(states=list(states.values()))

    @classmethod
    def write(cls, automaton: aut.FiniteAutomaton) -> str:
        """Write the automaton description in our custom format."""
        return (
            "Automaton:\n"
            + "".join(
                f"\t{s.name}{' final' if s.is_final else ''}\n"
                for s in automaton.states
            )
            + "\n"
            + "".join(
                f"\t{s.name} "
                f"-{t.symbol if t.symbol is not None else ''}->"
                f" {t.state}\n"
                for s in automaton.states for t in s.transitions
            )
        )


    
def write_dot(automaton: aut.FiniteAutomaton) -> str:
    """
    Write a dot representation of the automaton.

    Args:
        automaton: Automaton to print.

    Returns:
        Representation of the automaton in dot (Graphviz) language.

    """
    shape_dict = {
        True: "doublecircle",
        False: "circle",
    }

    def symbol_repr(symbol: Optional[str]) -> str:
        return "λ" if symbol is None else symbol

    return (
        "digraph {\n"
        "  rankdir=LR;\n"
        "\n"
        + "  node [shape = point]; __start_point__\n"
        + "".join(
            f"  {s.name}[shape={shape_dict[s.is_final]}]\n"
            for s in automaton.states
        )
        + "\n"
        + f"  __start_point__ -> {automaton.states[0].name}\n"
        + "".join(
            f"  {s.name} -> {t.state}"
            f"[label=\"{symbol_repr(t.symbol)}\"]\n"
            for s in automaton.states
            if s.transitions is not None
            for t in s.transitions 
        )
        + "}\n"
    )

