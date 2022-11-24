from __future__ import annotations

from collections import deque
from typing import (
    AbstractSet, Collection, MutableSet, Optional, Dict, List, Optional, Tuple
)
import copy

class RepeatedCellError(Exception):
    """Exception for repeated cells in LL(1) tables."""

class SyntaxError(Exception):
    """Exception for parsing errors."""

class Grammar:
    """
    Class that represents a grammar.

    Args:
        terminals: Terminal symbols of the grammar.
        non_terminals: Non terminal symbols of the grammar.
        productions: Dictionary with the production rules for each non terminal
          symbol of the grammar.
        axiom: Axiom of the grammar.

    """

    def __init__(
        self,
        terminals: AbstractSet[str],
        non_terminals: AbstractSet[str],
        productions: Dict[str, List[str]],
        axiom: str,
    ) -> None:
        if terminals & non_terminals:
            raise ValueError(
                "Intersection between terminals and non terminals "
                "must be empty.",
            )

        if axiom not in non_terminals:
            raise ValueError(
                "Axiom must be included in the set of non terminals.",
            )

        if non_terminals != set(productions.keys()):
            raise ValueError(
                f"Set of non-terminals and productions keys should be equal."
            )
        
        for nt, rhs in productions.items():
            if not rhs:
                raise ValueError(
                    f"No production rules for non terminal symbol {nt} "
                )
            for r in rhs:
                for s in r:
                    if (
                        s not in non_terminals
                        and s not in terminals
                    ):
                        raise ValueError(
                            f"Invalid symbol {s}.",
                        )

        self.terminals = terminals
        self.non_terminals = non_terminals
        self.productions = productions
        self.axiom = axiom
        print("productions", productions)
        self.first = self.precompute_first()

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}("
            f"terminals={self.terminals!r}, "
            f"non_terminals={self.non_terminals!r}, "
            f"axiom={self.axiom!r}, "
            f"productions={self.productions!r})"
        )

    def precompute_first(self) -> Dict[str, AbstractSet[str]]:
        """
        Method to compute the first set of all non-terminal symbols.

        Returns:
            Dictionary with the first set of all non-terminal symbols.
        """
        print("enter precompute_first")
        # init first with trivial cases
        first: Dict[str, AbstractSet[str]] = {
            nt: frozenset(
                rhs[0] for rhs in set(self.productions.get(nt))-{""}
                if rhs[0] in self.terminals
            ) | ({"",} if "" in self.productions.get(nt) else set())
            for nt in self.non_terminals
        }
        print("first", first)
        # productions with rhs starting with a non-terminal
        ntprods: List[Tuple] = [
            (nt, rhs) 
            for nt in self.non_terminals 
            for rhs in set(self.productions.get(nt))-{""}
            if rhs[0] in self.non_terminals
        ]

        # to check for changes in first
        prev_first: Dict[str, AbstractSet[str]] = {}

        def add_firsts(fdict: Dict[str, AbstractSet[str]], nt: str, rhs: str) -> None:
            if not rhs:
                return {""}
            elif rhs[0] in self.terminals:
                return {rhs[0]}
            else:
                return first[rhs[0]] - {""} | (
                    frozenset() if "" not in first[rhs[0]] 
                    else add_firsts(fdict, nt, rhs[1:])
                )

        while first != prev_first:
            prev_first = copy.copy(first)
            for nt, rhs in ntprods:
                first[nt] = first[nt] | add_firsts(first, nt, rhs)
        print("first", first)
        return first

    # TO-DO: Poner los tipos de AbstractSet ...
    def compute_first(self, sentence: str) -> AbstractSet[str]:
        """
        Method to compute the first set of a string.

        Args:
            str: string whose first set is to be computed.

        Returns:
            First set of str.
        """

        first = set()
        last_lambda = False

        if any(s not in self.terminals and s not in self.non_terminals for s in sentence):
            raise ValueError("Invalid symbol in sentence.")
        
        if sentence == "":
            return {""}
        
        for item in sentence:
            last_lambda = False

            if item in self.terminals:
                first.add(item)
                break
            else:
                aux_first = self.compute_first_non_terminal(item)
                first.update(aux_first-{""})
                if "" not in aux_first:
                    break
                else:
                    last_lambda = True

        if last_lambda:
            first.add("")

        return first

    def compute_first_non_terminal(self, symbol: str) -> AbstractSet[str]:
        """
        Method to compute the first set of a non-terminal symbol.

        Args:
            symbol: non-terminal whose first set is to be computed.

        Returns:
            First set of symbol.
        """
        return self.first.get(symbol)
        # first = set()

        # if symbol not in self.non_terminals:
        #     raise ValueError("Invalid symbol.")

        # for rhs in self.productions[symbol]:
        #     first.update(self.compute_first(rhs))

        # return first
    



    def compute_follow(self, symbol: str) -> AbstractSet[str]:
        """
        Method to compute the follow set of a non-terminal symbol.

        Args:
            symbol: non-terminal whose follow set is to be computed.

        Returns:
            Follow set of symbol.
        """

	# TO-DO: Complete this method for exercise 4...


    def get_ll1_table(self) -> Optional[LL1Table]:
        """
        Method to compute the LL(1) table.

        Returns:
            LL(1) table for the grammar, or None if the grammar is not LL(1).
        """

	# TO-DO: Complete this method for exercise 5...


    def is_ll1(self) -> bool:
        return self.get_ll1_table() is not None


class LL1Table:
    """
    LL1 table. Initially all cells are set to None (empty). Table cells
    must be filled by calling the method add_cell.

    Args:
        non_terminals: Set of non terminal symbols.
        terminals: Set of terminal symbols.

    """

    def __init__(
        self,
        non_terminals: AbstractSet[str],
        terminals: AbstractSet[str],
    ) -> None:

        if terminals & non_terminals:
            raise ValueError(
                "Intersection between terminals and non terminals "
                "must be empty.",
            )

        self.terminals: AbstractSet[str] = terminals
        self.non_terminals: AbstractSet[str] = non_terminals
        self.cells: Dict[str, Dict[str, Optional[str]]] = {nt: {t: None for t in terminals} for nt in non_terminals}

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}("
            f"terminals={self.terminals!r}, "
            f"non_terminals={self.non_terminals!r}, "
            f"cells={self.cells!r})"
        )

    def add_cell(self, non_terminal: str, terminal: str, cell_body: str) -> None:
        """
        Adds a cell to an LL(1) table.

        Args:
            non_terminal: Non termial symbol (row)
            terminal: Terminal symbol (column)
            cell_body: content of the cell 

        Raises:
            RepeatedCellError: if trying to add a cell already filled.
        """
        if non_terminal not in self.non_terminals:
            raise ValueError(
                "Trying to add cell for non terminal symbol not included "
                "in table.",
            )
        if terminal not in self.terminals:
            raise ValueError(
                "Trying to add cell for terminal symbol not included "
                "in table.",
            )
        if not all(x in self.terminals | self.non_terminals for x in cell_body):
            raise ValueError(
                "Trying to add cell whose body contains elements that are "
                "not either terminals nor non terminals.",
            )            
        if self.cells[non_terminal][terminal] is not None:
            raise RepeatedCellError(
                f"Repeated cell ({non_terminal}, {terminal}).")
        else:
            self.cells[non_terminal][terminal] = cell_body

    def analyze(self, input_string: str, start: str) -> ParseTree:
        """
        Method to analyze a string using the LL(1) table.

        Args:
            input_string: string to analyze.
            start: initial symbol.

        Returns:
            ParseTree object with either the parse tree (if the elective exercise is solved)
            or an empty tree (if the elective exercise is not considered).

        Raises:
            SyntaxError: if the input string is not syntactically correct.
        """

        #Comprobar que el input de entrada no contiene símbolos que no están en el alfabeto
        if any(terminal not in self.terminals for terminal in input_string):
            raise SyntaxError(
                "Input string contains symbols not included in the grammar.",
            )
        
        #Inicializar stack
        stack = list((start,"$"))

        while stack and input_string:

            next_symbol = input_string[0]
            stack_top = stack.pop(0)

            if stack_top in self.non_terminals:
                if self.cells[stack_top][next_symbol] is None:
                    raise SyntaxError(
                        f"There is no rule associated \
                        to ({stack_top}, {next_symbol}).")
                
                stack = list(self.cells[stack_top][next_symbol]) + stack
            else:
                if stack_top != next_symbol:
                    raise SyntaxError(
                        f"Syntax error. Expected {next_symbol}, found {stack_top}."
                    )
                #Avanzar el input
                input_string = input_string[1:]
               
          
        if input_string=="" and stack==[]:
            #TO-DO: Hacer ej opcional con arbol de parseo
            return ParseTree("")

        raise SyntaxError(
            f"Error during sintax analysis."
        )

	
    
    
class ParseTree():
    """
    Parse Tree.

    Args:
        root: root node of the tree.
        children: list of children, which are also ParseTree objects.
    """
    def __init__(self, root: str, children: Collection[ParseTree] = []) -> None:
        self.root = root
        self.children = children

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}({self.root!r}: {self.children})"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented
        return (
            self.root == other.root
            and len(self.children) == len(other.children)
            and all([x.__eq__(y) for x, y in zip(self.children, other.children)])
        )

    def add_children(self, children: Collection[ParseTree]) -> None:
        self.children = children
