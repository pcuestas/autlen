"""Evaluation of automata."""
from collections import defaultdict, deque
from typing import Set, TypedDict

from automata.automaton import FiniteAutomaton, State

class FiniteAutomatonEvaluator():
    """
    Definition of an automaton evaluator.

    Args:
        automaton: Automaton to evaluate.

    Attributes:
        current_states: Set of current states of the automaton.

    """

    automaton: FiniteAutomaton
    current_states: Set[State]

    #closures: TypedDict[State, Set[str]]

    def __init__(self, automaton: FiniteAutomaton) -> None:
        self.automaton = automaton
        current_states: Set[State] = {
            self.automaton.states[0],  
        }
        self._states_by_name = {state.name:state for state in self.automaton.states}
        transitions = sum([state.transitions for state in self.automaton.states], [])
        self._alphabet = set(transition.symbol for transition in transitions)
        self.closures = {}
        self._compute_closures()
        self._complete_lambdas(current_states)
        self.current_states = current_states


    def process_symbol(self, symbol: str) -> None:
        """
        Process one symbol.

        Args:
            symbol: Symbol to consume.

        """
        if symbol not in self._alphabet:
            raise Exception #TODO CREAR EXCEPCION

        new_states = set()

        for state in self.current_states:
            new_states.update(
                self._get_state(transition.state) 
                for transition in state.transitions 
                if transition.symbol==symbol
            )

        self._complete_lambdas(new_states)
        self.current_states = new_states
    
    def _compute_closures(self):
        '''
        Completes the self.closures dictionary with the closure 
        of each element.
        '''
        for closure_state in self.automaton.states:
            closure = set()
            expanding_states = set([closure_state])
    
            while expanding_states:
                closure.update(expanding_states)
                visited_states = set()
                for state in expanding_states:
                    visited_states.update(
                        self._get_state(transition.state) 
                        for transition in state.transitions 
                        if not transition.symbol
                    )
                expanding_states = visited_states

            self.closures[closure_state] = closure

    def _get_state(self, name:str) -> State :
        return self._states_by_name[name] 

    def _complete_lambdas(self, set_to_complete: Set[State]) -> None:
        """
        Add states reachable with lambda transitions to the set.

        Args:
            set_to_complete: Current set of states to be completed.
        """
        completed = set()

        for state in set_to_complete:
            completed.update(self.closures[state])
        
        set_to_complete.update(completed)
        
    def process_string(self, string: str) -> None:
        """
        Process a full string of symbols.

        Args:
            string: String to process.

        """
        for symbol in string:
            self.process_symbol(symbol)



    def is_accepting(self) -> bool:
        """Check if the current state is an accepting one."""

        return any([state.is_final for state in self.current_states])
        

    def accepts(self, string: str) -> bool:
        """
        Return if a string is accepted without changing state.

        Note: This function is NOT thread-safe.

        """
        old_states = self.current_states
        try:
            self.process_string(string)
            accepted = self.is_accepting()
        except: 
            accepted = False
        finally:
            self.current_states = old_states

        return accepted

