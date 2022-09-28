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

    closures: TypedDict[State, Set[str]]

    def __init__(self, automaton: FiniteAutomaton) -> None:
        self.automaton = automaton
        current_states: Set[State] = {
            self.automaton.states[0],  
        }
        self._compute_closures()
        self._complete_lambdas(current_states)
        self.current_states = current_states


    def process_symbol(self, symbol: str) -> None:
        """
        Process one symbol.

        Args:
            symbol: Symbol to consume.

        """

        new_states = set()

        for state in self.current_states:
            for transition in state.transitions:
                if transition.symbol == symbol:
                    new_states.add(transition.state)

        self._complete_lambdas(new_states)
        self.current_states = new_states

        #Lanzar excepcion si el simbolo no pertenece al abecedario 
    
    def _compute_closures(self):
        '''
        Completes the self.closures dictionary with the closure 
        of each element.
        '''

        for state in self.automaton.states:
            closure = set(state)
            round_states = set(state)
          
            while round_states:
                closure.add(round_states)
                new_states = set()
                for state in round_states:
                    new_states.add(transition.state for transition in 
                        filter(
                            lambda t : (not t.symbol), 
                            state.transitions
                        )
                    )
                round_states = new_states

            self.closures[state] = closure
    

    def _complete_lambdas(self, set_to_complete: Set[State]) -> None:
        """
        Add states reachable with lambda transitions to the set.

        Args:
            set_to_complete: Current set of states to be completed.
        """
        completed = set()

        for state in set_to_complete:
            completed.union(self.closures[state])
        
        set_to_complete.union(completed)
        
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
        finally:
            self.current_states = old_states

        return accepted

