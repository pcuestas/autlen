"""General utilities to work with automatas."""
import re
from collections import defaultdict, deque
from typing_extensions import Final

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

def is_deterministic(automaton: aut.FiniteAutomaton) -> bool:
    """
    Check if an automaton is deterministic.

    Args:
        automaton: Automaton to check.

    Returns:
        ``True`` if the automaton is deterministic.
        ``False`` otherwise.

    """
    checked_origins = set()

    for s in automaton.states:
        for t in s.transitions:
            if t.symbol is None:
                return False

            origin = (s, t.symbol)
            if origin in checked_origins:
                return False

            checked_origins.add(origin)

    return True

def deterministic_automata_isomorphism(
    automaton1: aut.FiniteAutomaton,
    automaton2: aut.FiniteAutomaton,
) -> Optional[Mapping[aut.State, aut.State]]:
    """Check if two deterministic automata are the same but renamed."""
    if not is_deterministic(automaton1) or not is_deterministic(automaton2):
        raise ValueError("Automata are not deterministic")

    if len(automaton1.states) != len(automaton2.states):
        return None

    for s1, s2 in zip(automaton1.states, automaton2.states):
        if len(s1.transitions) != len(s2.transitions):
            return None

    equiv_map: Dict[aut.State, aut.State] = {}
    pending = deque({(automaton1.states[0], automaton2.states[0])})

    transition_map1: DefaultDict[
        aut.State,
        Dict[Optional[str], aut.State],
    ] = defaultdict(dict)
    for s in automaton1.states:
        for t in s.transitions:
            transition_map1[s][t.symbol] = automaton1.name2state[t.state]

    transition_map2: DefaultDict[
        aut.State,
        Dict[Optional[str], aut.State],
    ] = defaultdict(dict)
    for s in automaton2.states:
        for t in s.transitions:
            transition_map2[s][t.symbol] = automaton2.name2state[t.state]

    while pending:
        state1, state2 = pending.pop()
        if state1.is_final is not state2.is_final:
            return None

        equiv_state = equiv_map.get(state1)
        if equiv_state:
            if equiv_state is not state2:
                return None

        else:
            equiv_map[state1] = state2
            transitions1 = transition_map1[state1]
            transitions2 = transition_map2[state2]
            if len(transitions1) != len(transitions2):
                return None

            for symbol, final1 in transitions1.items():
                final2 = transitions2.get(symbol)
                if final2 is None:
                    return None

                pending.appendleft((final1, final2))

    return equiv_map
