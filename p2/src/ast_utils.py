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
        return ast.Subscript(
            value=ast.Name(id='data', ctx=ast.Load()),
            slice=ast.Index(value=ast.Constant(value=node.id)),
            ctx=node.ctx
        )

            

class ASTUnroll(ast.NodeTransformer):

    def generic_visit(self, node: ast.AST) -> ast.AST:
        if isinstance(node, ast.For):
            return self.visit_For(node)
        else:
            return

    def visit_For(self, node: ast.For) -> ast.For:
        if isinstance(node.iter, ast.Call):
            if isinstance(node.iter.func, ast.Name):
                if node.iter.func.id == "range":
                    if len(node.iter.args) == 1:
                        return self.unroll_for(node, node.iter.args[0])
                    elif len(node.iter.args) == 2:
                        return self.unroll_for(node, node.iter.args[1])
                    elif len(node.iter.args) == 3:
                        return self.unroll_for(node, node.iter.args[2])
        return node

    def unroll_for(self, node: ast.For, n: int) -> ast.For:
        body = []
        for i in range(n):
            body.append(ast.copy_location(ast.copy(node.body), node.body))
        return ast.copy_location(ast.copy(body), body)