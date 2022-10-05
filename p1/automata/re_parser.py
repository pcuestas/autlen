"""Conversion from regex to automata."""
from typing import List, Dict, Set

from automata.automaton import FiniteAutomaton, State, Transition
from automata.utils import AutomataFormat

import copy 

def _re_to_rpn(re_string: str) -> str:
    """
    Convert re to reverse polish notation (RPN).

    Does not check that the input re is syntactically correct.

    Args:
        re_string: Regular expression in infix notation.

    Returns:
        Regular expression in reverse polish notation.

    """
    stack: List[str] = []
    rpn_string = ""
    for x in re_string:
        if x == "+":
            while len(stack) > 0 and stack[-1] != "(":
                rpn_string += stack.pop()
            stack.append(x)
        elif x == ".":
            while len(stack) > 0 and stack[-1] == ".":
                rpn_string += stack.pop()
            stack.append(x)
        elif x == "(":
            stack.append(x)
        elif x == ")":
            while stack[-1] != "(":
                rpn_string += stack.pop()
            stack.pop()
        else:
            rpn_string += x

    while len(stack) > 0:
        rpn_string += stack.pop()

    return rpn_string



class REParser():
    """Class for processing regular expressions in Kleene's syntax."""

    state_counter: int

    def __init__(self) -> None:
        self.state_counter = 0

    def _create_automaton_empty(
        self,
    ) -> FiniteAutomaton:
        """
        Create an automaton that accepts the empty language.

        Returns:
            Automaton that accepts the empty language.

        """
        return  AutomataFormat.read(
            """
                Automaton:
                    0 
            """
        )
    


    def _rename_states(
        self, 
        states: List[State], 
        index: int = 0
    )-> int:
    
        state_dict: Dict[str, str] = {} #nombre antiguo:nombre nuevo
        
        for state in states:
            state_dict[state.name] = str(index)
            index += 1

        for state in states:
            state.name = state_dict[state.name]
            for transition in state.transitions:
                transition.state = state_dict[transition.state]
                
        return index

    def _get_final_states(
        self, 
        states: List[State]
    ) -> Set[State]:
        return set(
            state 
            for state in states 
            if state.is_final
        )
        

    def _create_automaton_lambda(
        self,
    ) -> FiniteAutomaton:
        """
        Create an automaton that accepts the empty string.

        Returns:
            Automaton that accepts the empty string.

        """
        return  AutomataFormat.read(
            """
                Automaton:
                    0 final
            """
        )


    def _create_automaton_symbol(
        self,
        symbol: str,
    ) -> FiniteAutomaton:
        """
        Create an automaton that accepts one symbol.

        Args:
            symbol: Symbol that the automaton should accept.

        Returns:
            Automaton that accepts a symbol.

        """
        return  AutomataFormat.read(
            f"""
                Automaton:
                    0 
                    1 final
                    0-{symbol}->1
            """
        )


    def _create_automaton_star(
        self,
        automaton: FiniteAutomaton,
    ) -> FiniteAutomaton:
        """
        Create an automaton that accepts the Kleene star of another.

        Args:
            automaton: Automaton whose Kleene star must be computed.

        Returns:
            Automaton that accepts the Kleene star.

        """
        
        new_states = copy.deepcopy(automaton.states)
        final_states_index = self._rename_states(new_states)
        final_states = self._get_final_states(new_states)
        
        #Estado final sumidero.
        final_state = State(name=str(final_states_index), is_final=True)
        
        for state in final_states:
            state.add_transitions([Transition(symbol=None,state=final_state.name)])

        new_states[0].add_transitions([Transition(symbol=None,state=final_state.name)])
        final_state.add_transitions([Transition(symbol=None,state=new_states[0].name)])

        return FiniteAutomaton(new_states + [final_state])

    def _create_automaton_union(
        self,
        automaton1: FiniteAutomaton,
        automaton2: FiniteAutomaton,
    ) -> FiniteAutomaton:
        """
        Create an automaton that accepts the union of two automata.

        Args:
            automaton1: First automaton of the union.
            automaton2: Second automaton of the union.

        Returns:
            Automaton that accepts the union.

        """
        
        initial_state = State('0', is_final=False)
        
        states1 = copy.deepcopy(automaton1.states)
        index = self._rename_states(states1, index=1)
        index_inital_automaton2 = index

        states2 = copy.deepcopy(automaton2.states)
        index = self._rename_states(states2, index=index)

        initial_state.add_transitions([
            Transition(symbol=None, state='1'),
            Transition(symbol=None, state=str(index_inital_automaton2))
        ])

        return FiniteAutomaton([initial_state] + states1 + states2) 

    def _create_automaton_concat(
        self,
        automaton1: FiniteAutomaton,
        automaton2: FiniteAutomaton,
    ) -> FiniteAutomaton:
        """
        Create an automaton that accepts the concatenation of two automata.

        Args:
            automaton1: First automaton of the concatenation.
            automaton2: Second automaton of the concatenation.

        Returns:
            Automaton that accepts the concatenation.

        """
       
        states1 = copy.deepcopy(automaton1.states)
        index = self._rename_states(states1)

        final_states1 = self._get_final_states(states1)

        states2 = copy.deepcopy(automaton2.states)
        index = self._rename_states(states2, index=index)

        for state in final_states1:
            state.add_transitions([
                Transition(symbol=None,state=states2[0].name)
            ])
            state.is_final=False

        return FiniteAutomaton(states1 + states2)

    def create_automaton(
        self,
        re_string: str,
    ) -> FiniteAutomaton:
        """
        Create an automaton from a regex.

        Args:
            re_string: String with the regular expression in Kleene notation.

        Returns:
            Automaton equivalent to the regex.

        """
        if not re_string:
            return self._create_automaton_empty()
        
        rpn_string = _re_to_rpn(re_string)

        stack: List[FiniteAutomaton] = []
        self.state_counter = 0
        for x in rpn_string:
            if x == "*":
                aut = stack.pop()
                stack.append(self._create_automaton_star(aut))
            elif x == "+":
                aut2 = stack.pop()
                aut1 = stack.pop()
                stack.append(self._create_automaton_union(aut1, aut2))
            elif x == ".":
                aut2 = stack.pop()
                aut1 = stack.pop()
                stack.append(self._create_automaton_concat(aut1, aut2))
            elif x == "λ":
                stack.append(self._create_automaton_lambda())
            else:
                stack.append(self._create_automaton_symbol(x))

        return stack.pop()
