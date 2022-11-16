import ast
from ast import (
    AST, iter_fields
)
from typing import Any

MY_ATTRIBUTES = ["name","returns","vararg","kwarg",]

class ASTNestedForCounter(ast.NodeVisitor):

    def generic_visit(self, node: AST) -> int:
        maxdepth = 0
        print(type(node).__name__)
        for _, value in iter_fields(node):
            if isinstance(value, list) and value:
                maxdepth = max(
                    maxdepth, 
                    *[self.item_visit(item) for item in value]
                )            
            elif value:
                maxdepth = max(maxdepth, self.item_visit(value))
        
        return maxdepth

    def item_visit(self, node: Any) -> int:
        if isinstance(node, ast.For):
            return self.visit_For(node)
        elif isinstance(node, AST):
            return self.generic_visit(node)
        else:
            return 0

    def visit_For(self, node: ast.For):
        return 1 + self.generic_visit(node)


class ASTDotVisitor(ast.NodeVisitor): 

    idcounter : int


    attributes : dict()
    
    def generic_visit(self, node: AST) -> Any:
        self.idcounter = 0
        print("digraph {")
        self.rec_visit(node)
        print("}")


    
    def rec_visit(self, node: AST) -> None:
        pid = self.idcounter
        print(
            's{}[label="{}({})", shape=box]'.
            format(
                self.idcounter, type(node).__name__, self.my_vars(node)
            )
        )
        for field, value in iter_fields(node):
            if isinstance(value, list) and value:
                for item in value:
                    self.print_item(field, item, pid)
                    
            elif isinstance(value, AST):
                self.print_item(field, value, pid)

    def print_item(self, field: str, node: AST, pid: int)->Any:

        self.idcounter += 1
        print(
            f's{pid} -> s{self.idcounter}[label="{field}"]'
        )
        self.rec_visit(node)

    
    def my_vars(self, object: Any):
        return ",".join(
            f"{key}='{value}'" 
            for key,value in vars(object) 
            if key in MY_ATTRIBUTES
        )