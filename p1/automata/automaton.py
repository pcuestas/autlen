"""Automaton implementation."""
from typing import (
    Optional,
    Set,
    List,
    Dict,
    FrozenSet,
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
        alphabet: Set[str] = utils.alphabet(self.states)
        closures: Dict[State, FrozenSet[State]] = utils.compute_closures(self)

        # open_set: contains the visited (new)states, which are frozensets
        open_set: Set[FrozenSet[State]] = set([closures[self.states[0]]]) 
        # closed_set contains the expanded (new)states, which are frozensets
        closed_set: Set[FrozenSet[State]] = set()

        in_construction_automaton: Dict[FrozenSet[State], Dict[str, FrozenSet[State]]] = {}
        empty_set_flag: bool = False

        while open_set:
            current_set = open_set.pop() 
            if not current_set: 
                empty_set_flag = True
            elif current_set not in closed_set:
                self._to_det_expand_set(
                    current_set=current_set, 
                    alphabet=alphabet, 
                    closures=closures, 
                    open_set=open_set, 
                    closed_set=closed_set, 
                    in_construction_automaton=in_construction_automaton
                )

        # new states:
        new_automaton_states: List[State] = utils.states_from_in_construction_automaton(
            in_construction_automaton=in_construction_automaton,
            empty_set_flag=empty_set_flag,
            alphabet=alphabet
        )        

        return FiniteAutomaton(new_automaton_states)

    def _to_det_expand_set(
        self, 
        current_set: FrozenSet[State], 
        alphabet: Set[str], 
        closures: Dict[State, FrozenSet[State]],
        open_set: Set[FrozenSet[State]] ,
        closed_set: Set[FrozenSet[State]],
        in_construction_automaton: Dict[FrozenSet[State], Dict[str, FrozenSet[State]]] 
    )-> None:
        '''
        Fills the dictionary in_construction_automaton[current_set] 
        with all the possible transitions from current_set. 
        The transitions we talk about here are of the form:
            'symbol': 'set of states reachable from current_set after consuming symbol'
        '''
        closed_set.add(current_set)
        in_construction_automaton[current_set] = {}

        for symbol in alphabet:
            set_after_symbol: FrozenSet[State] = self._to_det_get_next_set(
                current_set=current_set,
                symbol=symbol,
                closures=closures
            )
            in_construction_automaton[current_set][symbol] = set_after_symbol
            open_set.add(set_after_symbol)

    def _to_det_get_next_set(
        self,
        current_set: FrozenSet[State], 
        symbol: str,
        closures: Dict[State, FrozenSet[State]],
    )-> FrozenSet[State]:
        '''
        Returns all states that are reachable from 
        current_set after consuming the symbol.
        '''
        # all possible transitions from current set of states:
        transitions: List[Transition] = sum([state.transitions for state in current_set], [])
        # set of states that we can transition to using the symbol:
        next_states_set: Set[State] = set(
            self.name2state[transition.state]
            for transition in transitions
            if transition.symbol == symbol
        )
        # return the closure of the set of states that 
        # we can transition to with the symbol
        return utils.closure_of_set(states_set=next_states_set, closures=closures)


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



class utils:
    @staticmethod
    def alphabet(
        states: List[State]
    ) -> Set[str]:
        '''
        Returns the alphabet of the transitions of all the states.
        That is, every symbol there is a transition for.
        '''
        # all transitions of every state
        transitions: list[Transition] = sum(
            [state.transitions for state in states], 
            []
        )
        # the alphabet contains every symbol that appears in a transition 
        return set(transition.symbol for transition in transitions if transition.symbol)

    @staticmethod
    def compute_closures(
        automaton: FiniteAutomaton
    ) -> Dict[State, FrozenSet[State]] :
        '''
        Completes a closures dictionary with 
        the closure of each state of the automaton.
        The return dict is:
            - Key: state
            - Value: set of states in the key's closure
        '''
        closures: Dict[State, FrozenSet[State]] = {} 
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

            closures[closure_state] = frozenset(closure)

        return closures
    
    @staticmethod
    def closure_of_set(
        states_set: Set[State],
        closures: Dict[State, FrozenSet[State]]
    ) -> FrozenSet[State] :
        '''
        Receives a set (states_set) and a dictionary with 
        the closures of each state.
        Returns the closure of states_set.
        '''
        completed: Set[State] = set()
        for state in states_set:
            completed.update(closures[state])
        return frozenset(completed)

    @staticmethod
    def name_of_states_set(
        states_set: FrozenSet[State]
    )-> str:
        if not states_set:
            return 'empty'
        names = [state.name for state in states_set]
        names.sort()
        return "|".join(names)

    @staticmethod
    def dict_to_transitions(
        transitions_dict: Dict[str, FrozenSet[State]]
    )-> List[Transition]:
        transitions: List[Transition] = []
        for symbol, states_set in transitions_dict.items():
            transitions.append(
                Transition(
                    symbol=symbol,
                    state=utils.name_of_states_set(states_set)
                )
            )
        return transitions

    @staticmethod
    def states_from_in_construction_automaton(
        in_construction_automaton: Dict[FrozenSet[State], Dict[str, FrozenSet[State]]],
        empty_set_flag: bool,
        alphabet: Set[str]
    )-> List[State]:
        '''
        Receives a dictionary of the form of in_costruction_automaton
        and reutrns a list of states: assigning each FrozenSet[State] 
        to a state, and converting dictionaries of type 
        Dict[str, FrozenSet[State]] into lists of transitions.
        The empty_set_flag indicates if there is any transition to the 
        empty (frozen)set, in which case an 'empty' state will be added.
        '''
        new_automaton_states: List[State] = []

        for states_set, transitions_dict in in_construction_automaton.items():
            new_state: State = State(
                name=utils.name_of_states_set(states_set), 
                is_final=any(state.is_final for state in states_set)
            )
            # transitions:
            new_state.add_transitions(utils.dict_to_transitions(transitions_dict))
            new_automaton_states.append(new_state)

        if empty_set_flag:
            empty_state = State(name='empty', is_final=False)
            empty_state.add_transitions([
                Transition(symbol=symbol, state='empty') 
                for symbol in alphabet
            ])
            new_automaton_states.append(empty_state)

        return new_automaton_states