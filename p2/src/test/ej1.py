

import ast
import inspect
import pydot
import os
from src.ast_utils import ASTNestedForCounter, ASTDotVisitor
from typing import Any
from src.test.redirect_stdout import RedirectedStdout

pics_dir: str = ''


def set_up() -> None:
    global pics_dir
    pics_dir = os.path.dirname(os.path.realpath(__file__))
    pics_dir = pics_dir[:pics_dir.rfind('p2') + 2] + '/pics/'
    if not os.path.exists(pics_dir):
        os.makedirs(pics_dir)


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


def fun3():
    for _ in "asd":
        for _ in "abc":
            for _ in "abc":
                pass 
            for _ in "abc":
                for _ in "abc":
                    for _ in "abc":
                        pass
    for _ in "asd":
        for _ in "asd":
            for _ in "abc":
                pass
            for _ in "asd":
                for _ in "asd":
                    pass


def print_if_pos(num):
    if num > 0:
        print(num)


def main_a() -> None:
    print("##################################################################")
    print("Beginning exercise 1, (a) ...")
    counter = ASTNestedForCounter()

    def check_fun(fun, expected):
        source = inspect.getsource(fun)
        my_ast = ast.parse(source)
        maxdepth = counter.visit(my_ast)
        assert expected == maxdepth, f"Expected {expected}, got {maxdepth}"

    check_fun(fun1, 1)
    check_fun(fun2, 3)
    check_fun(fun3, 5)

    print("Ending exercise 1, (a). Everything is OK.")


def main_b() -> None:
    print("##################################################################")
    print("Beginning exercise 1, (b) ...")
    counter = ASTDotVisitor()
    source = inspect.getsource(print_if_pos)
    my_ast = ast.parse(source)

    with RedirectedStdout() as out:
        counter.visit(my_ast)

    # print(out)
    graph, = pydot.graph_from_dot_data(str(out))
    graph.write_png(pics_dir + 'ex1b.png')

    print(f"Ending exercise 1, (b). Output written to {pics_dir}ex1b.png")


if __name__ == '__main__':
    set_up()
    main_a()
    main_b()
