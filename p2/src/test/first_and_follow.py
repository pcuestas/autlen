
from src.utils import GrammarFormat

def test_first(grammar, symbol):
    print(
        f"First({symbol}) = {set(grammar.compute_first(symbol))}"
    )
def test_follow(grammar, symbol):
    print(
        f"Follow({symbol}) = {set(grammar.compute_follow(symbol))}"
    )

def test_grammar(grammar_str: str) -> None:
    grammar = GrammarFormat.read(grammar_str)
    
    for nt in grammar.non_terminals:
        test_first(grammar, nt)
    for nt in grammar.non_terminals:
        test_follow(grammar, nt)


# grammar_str = """
#     E -> TX
#     X -> +E
#     X ->
#     T -> iY
#     T -> (E)
#     Y -> *T
#     Y ->
# """

grammar_str = """
    X -> I*AD
    I -> A*I
    I -> a
    A -> a
    I -> 
    A -> 
    D -> *
    D ->
    A -> aa*A
"""

if __name__ == '__main__':
    
    test_grammar(grammar_str)