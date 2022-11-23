import ast
from ast import (
    AST, iter_fields
)
from typing import Any, Union, List
import copy

ATTRIBUTES = [
    "name", "returns", "vararg", "kwarg", "type_comment", "arg", "annotation",
    "value", "kind", "id",
]


class ASTNestedForCounter(ast.NodeVisitor):

    def generic_visit(self, node: AST) -> int:
        maxdepth = 0
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

    def visit_For(self, node: ast.For) -> int:
        return 1 + self.generic_visit(node)


class ASTDotVisitor(ast.NodeVisitor):

    idcounter: int

    def generic_visit(self, node: AST) -> Any:
        self.idcounter = 0
        print("digraph {")
        self.visit_node(node)
        print("}")

    def visit_node(self, node: AST) -> None:
        nodeid = self.idcounter
        print('s{}[label="{}({})", shape=box]'.
              format(nodeid, type(node).__name__, self.my_vars(node)))

        for field, value in iter_fields(node):
            if isinstance(value, list) and value:
                for item in value:
                    self.visit_child_node(field, item, nodeid)
            elif isinstance(value, AST):
                self.visit_child_node(field, value, nodeid)

    def visit_child_node(self, field: str, node: AST, parentid: int) -> Any:
        self.idcounter += 1
        print(f's{parentid} -> s{self.idcounter}[label="{field}"]')
        self.visit_node(node)

    def my_vars(self, object: Any) -> str:
        return ", ".join(
            f"{key}='{value}'"
            for key, value in iter_fields(object)
            if not isinstance(value, (ast.AST, list))
        )


    # name.id string
    # ctx=Load() 
class ASTReplacerVar(ast.NodeTransformer):

    ast_tree: ast.AST
    variable_name: str

    def __init__(self, variable_name: str, ast_tree: ast.AST) -> None:
        self.ast_tree = ast_tree
        self.variable_name = variable_name

    def visit_Name(self, node: ast.Name) -> ast.AST:
        if node.id == self.variable_name and isinstance(node.ctx,ast.Load):
            return self.ast_tree
        return node

            

class ASTUnroll(ast.NodeTransformer):

    def visit_For(self, node: ast.For) -> Union[List[Any], ast.For]:
        ast.NodeTransformer.generic_visit(self, node)
        
        if not (
            isinstance(node.iter, ast.List) and 
            isinstance(node.target, ast.Name)
        ):
            return node
        # en caso iter tipo List y target tipo Name:

        # new_body es el nuevo cuerpo que sustituirá al for 
        new_body = []
        # para cada elemento de la lista:
        for element in node.iter.elts:
            # sustituir la variable del for por el elemento de la lista
            # que se está recorriendo en cada iteración:
            replacer = ASTReplacerVar(node.target.id, element)
            block = copy.deepcopy(node.body)
            for statement in block:
                replacer.visit(statement)
            # añadir el bloque de código a la lista de nuevo código
            new_body.extend(block)

        return new_body