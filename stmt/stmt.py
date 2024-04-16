from expr.expr import Expr
from lox_token import Token
from abc import abstractmethod

class StmtVisitor:
    @abstractmethod
    def visit_expression_stmt(self, stmt): pass

    @abstractmethod
    def visit_print_stmt(self, stmt): pass 

    @abstractmethod
    def visit_declaration_stmt(self, stmt): pass


class Stmt:
    def accept(self, visitor: StmtVisitor):
        pass

class Expression(Stmt):
    def __init__(self, expr: Expr):
        self.expression = expr

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_expression_stmt(self)

class Print(Stmt):
    def __init__(self, expr: Expr):
        self.expression = expr

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_print_stmt(self)

class Var(Stmt):
    def __init__(self, name: Token, initializer: Expr):
        self.name = name
        self.initializer = initializer

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_declaration_stmt(self)