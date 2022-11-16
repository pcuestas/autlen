

import ast
import inspect
from src.ast_utils import ASTNestedForCounter, ASTDotVisitor


def fun1(p):
    for a in [10, 20, 30]:
        print(a)
    for x in range(10):
        print(x)

        
def fun2(p):
    for a in [10, 20, 30]:
        print(a)
    for i in [10, 20, 30]:
        for j in [10, 20, 30]:
            for k in [10, 20, 30]:
                print(i)

def print_if_pos(num):
    if num > 0:
        print (num)

def main_a() -> None:

    print("Beginning exercise 1, (a) ...")
    counter = ASTNestedForCounter()
    source = inspect.getsource(fun1)
    my_ast = ast.parse(source)
    print("Maximum number of nested for loops:", counter.visit(my_ast))
    
    # Should print 1
    source = inspect.getsource(fun2)
    my_ast = ast.parse(source)
    print("Maximum number of nested for loops:", counter.visit(my_ast))
    # Should print 3

    print("Ending exercise 1, (a) ...")


def main_b() -> None:

    print("Beginning exercise 1, (b) ...")
    counter = ASTDotVisitor()
    source = inspect.getsource(print_if_pos)
    my_ast = ast.parse(source)
    print("Grafo: \n", counter.visit(my_ast))
    
    print("Ending exercise 1, (b) ...")

if __name__ == '__main__':
    # main_a()
    main_b()