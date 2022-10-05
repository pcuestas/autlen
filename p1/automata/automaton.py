"""Automaton implementation."""
from typing import (
    Optional,
    Set,
    List,
    Dict,
)

class State():
    """
    Definition of an automaton state. 

    Args:
        name: Name of the state.
        is_final: Whether the state is a final state or not.
        transitions: The list of transitions starting at this state.

    """

    name: str
    is_final: bool
    transitions: List['Transition']

    def __init__(self, name: str, is_final: bool = False) -> None:
        self.name = name
        self.is_final = is_final
        self.transitions = []

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented

        return (
            self.name == other.name
        )

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}({self.name!r}, is_final={self.is_final!r}, transitions={self.transitions!r})"
        )

    def __hash__(self) -> int:
        return hash(self.name)

    def add_transitions(self, transitions: List['Transition']) -> None:
        """
        Convert to set and back to list to avoid repeated transitions.
        """
        self.transitions.extend(transitions)
        self.transitions = list(set(self.transitions))
    


class Transition():
    """
    Definition of an automaton transition. Since all transitions 
    'belong' to a given state, the initial state is not specified. 

    Args:
        symbol: Symbol consumed in the transition.
            ``None`` for a lambda transition.
        state: Name of the final state of the transition.

    """

    symbol: Optional[str]
    state: str

    def __init__(
        self,
        symbol: Optional[str],
        state: str,
    ) -> None:
        self.symbol = symbol
        self.state = state

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented

        return (
            self.symbol == other.symbol
            and self.state == other.state
        )

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}("
            f"{self.symbol!r}, {self.state!r})"
        )

    def __hash__(self) -> int:
        return hash((self.symbol, self.state))




class FiniteAutomaton():
    """
    Definition of an automaton.

    Args:
        states: List of states of the automaton. The first state in the 
                list is the initial state.

    """

    states: List[State]
    name2state: Dict[str, State]
    
    def __init__(
        self,
        states: List[State],
    ) -> None:
        """
        Check that there are no states with the same name.
        """
        if len(set(states)) != len(states):
            raise ValueError(
                "There are states with the same name",
            )
        """
        Check that the states in all transitions exist.
        """
        if not {t.state for s in states for t in s.transitions}.issubset({s.name for s in states}):
            raise ValueError(
                "There are transitions to an undefined state",
            )
        
        self.states = states
        self.name2state = {s.name: s for s in self.states}


    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}("
            f"states={self.states!r}, "
        )


    def to_deterministic(self) -> 'FiniteAutomaton':
        """
        Return a equivalent deterministic automaton.

        Returns:
            Equivalent deterministic automaton.

        """
        #---------------------------------------------------------------------

        '''
        dict[set, dict[symbol, set]] // después traducimos set==> state
        '''
        # TO DO: Implement this method...
        
        raise NotImplementedError("This method must be implemented.")        
        #---------------------------------------------------------------------


    def to_minimized(self) -> 'FiniteAutomaton':
        """
        Return a equivalent minimal automaton.

        Returns:
            Equivalent minimal automaton.

        """
        #---------------------------------------------------------------------
        # TO DO: Implement this method...
        
        raise NotImplementedError("This method must be implemented.")        
        #---------------------------------------------------------------------



class utils():
    def alphabet(states: List[State]) -> Set[str]:
        '''returns the alphabet of the transitions of all the states'''
        # all transitions of every state
        transitions: list[Transition] = sum(
            [state.transitions for state in states], 
            []
        )
        # the alphabet contains every symbol that appears in a transition 
        return set(transition.symbol for transition in transitions)

    def compute_closures(automaton: FiniteAutomaton) -> Set[State]:
        '''
        Completes a closures dictionary with 
        the closure of each state of the automaton.
        The return dict is:
            - Key: state
            - Value: set of states in the key's closure
        '''
        closures: Dict[State, Set[State]] = {} 
        for closure_state in automaton.states:
            closure = set()
            expanding_states: set[State] = set([closure_state])
    
            while expanding_states:
                closure.update(expanding_states)
                visited_states: set[State] = set()
                for state in expanding_states:
                    visited_states.update(
                        automaton.name2state[transition.state]
                        for transition in state.transitions 
                        if not transition.symbol and automaton.name2state[transition.state] not in closure
                    )
                expanding_states = visited_states

            closures[closure_state] = closure

        return closures


