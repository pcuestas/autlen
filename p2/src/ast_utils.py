import ast
from ast import (
    AST, iter_fields
)
from typing import Any
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

    def __init__(self, variable_name: ast.Name, ast_tree: ast.AST) -> None:
        self.ast_tree = ast_tree
        self.variable_name = variable_name

    def visit_Name(self, node):
        if node.id == self.variable_name and isinstance(node.ctx,ast.Load):
            return self.ast_tree
        return node

            

class ASTUnroll(ast.NodeTransformer):

    def visit_For(self, node: ast.For) -> ast.For:
        ast.NodeTransformer.generic_visit(self, node)
        
        if not (
            isinstance(node.iter, ast.List) and 
            isinstance(node.target, ast.Name)
        ):
            return node
        # en caso iter tipo List y target tipo Name:

        # quitar el for y sustituirla por un bloque de código desplegado
        # con los elementos de la lista:
        # for i in [1, 2, 3]:
        #     print(i)
        # 
        # se sustituye por:
        # print(1)
        # print(2)
        # print(3)

        # 1. copiar el bloque de código dentro del for:
        block = copy.deepcopy(node.body)
        # 2. sustituir la variable del for por el elemento de la lista
        #    que se está recorriendo en cada iteración:
        for element in node.iter.elts:
            # 3. sustituir la variable del for por el elemento de la lista
            #    que se está recorriendo en cada iteración:
            replacer = ASTReplacerVar(node.target, element)
            for statement in block:
                replacer.visit(statement)
            # 4. añadir el bloque de código al AST:
            node.body.extend(block)

        # 5. eliminar el for:
        # node.iter = ast.Constant(value=None)
        # node.target = ast.Constant(value=None)
        # node.body = []

        return node