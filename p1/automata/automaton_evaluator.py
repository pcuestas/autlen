"""Evaluation of automata."""
from typing import Set, Dict, FrozenSet

from automata.automaton import FiniteAutomaton, State, utils

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

    closures: Dict[State, FrozenSet[State]]
    _alphabet: Set[str]

    def __init__(self, automaton: FiniteAutomaton) -> None:
        self.automaton = automaton
        current_states: Set[State] = {
            self.automaton.states[0],  
        }
        self._alphabet = utils.alphabet(automaton.states)
        # self.closures is a dictionary that contains states as keys, and the set of states in its closure as values
        self.closures = utils.compute_closures(automaton)

        self._complete_lambdas(current_states)
        self.current_states = current_states


    def process_symbol(self, symbol: str) -> None:
        """
        Process one symbol.

        Args:
            symbol: Symbol to consume.

        """
        if symbol not in self._alphabet:
            raise InvalidSymbol(f"'{symbol}' is not in the alphabet.")

        new_states: set[State] = set()

        for state in self.current_states:
            new_states.update(
                self._get_state(transition.state) 
                for transition in state.transitions 
                if transition.symbol==symbol
            )

        self._complete_lambdas(new_states)
        self.current_states = new_states

    def _get_state(self, name:str) -> State :
        return self.automaton.name2state[name] 

    def _complete_lambdas(self, set_to_complete: Set[State]) -> None:
        """
        Add states reachable with lambda transitions to the set.

        Args:
            set_to_complete: Current set of states to be completed.
        """
        completed: Set[State] = set()

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
        return any(state.is_final for state in self.current_states)
        

    def accepts(self, string: str) -> bool:
        """
        Return if a string is accepted without changing state.

        Note: This function is NOT thread-safe.

        """
        old_states = self.current_states
        try:
            self.process_string(string)
            accepted = self.is_accepting()
        except InvalidSymbol:
            accepted = False # if there is an error while processing
        finally:
            self.current_states = old_states

        return accepted


class InvalidSymbol(Exception):
    """
    Exception used when the processed symbol 
    is not in the alphabet.
    """