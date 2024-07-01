from expr import Expr
from lox_token import Token
from abc import ABC, abstractmethod
from typing import List

class StmtVisitor(ABC):
    @abstractmethod
    def visit_expression_stmt(self, stmt): pass

    @abstractmethod
    def visit_function_stmt(self, stmt): pass

    @abstractmethod
    def visit_if_stmt(self, stmt): pass

    @abstractmethod
    def visit_print_stmt(self, stmt): pass 

    @abstractmethod
    def visit_block_stmt(self, stmt): pass

    @abstractmethod
    def visit_declaration_stmt(self, stmt): pass

    @abstractmethod
    def visit_while_stmt(self, stmt): pass


class Stmt:
    def accept(self, visitor: StmtVisitor):
        pass

class Expression(Stmt):
    def __init__(self, expr: Expr):
        self.expression = expr

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_expression_stmt(self)

class Function(Stmt):
    def __init__(self, name: Token, parameters: List[Token], body: List[Stmt]): 
        self.name = name
        self.parameters = parameters
        self.body = body

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_function_stmt(self)

class If(Stmt):
    def __init__(self, condition: Expr, then_branch: Stmt, else_branch: Stmt = None):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_if_stmt(self)

class Print(Stmt):
    def __init__(self, expr: Expr):
        self.expression = expr

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_print_stmt(self)

class Block(Stmt):
    def __init__(self, statements: List[Stmt]):
        self.statements = statements

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_block_stmt(self)

class Var(Stmt):
    def __init__(self, name: Token, initializer: Expr):
        self.name = name
        self.initializer = initializer

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_declaration_stmt(self)

class While(Stmt):
    def __init__(self, condition: Expr, body: Stmt):
        self.condition = condition
        self.body = body

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_while_stmt(self)