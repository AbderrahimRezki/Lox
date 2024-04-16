from lox_token import Token, TokenType
from errors import Error
from expr.expr import *
from stmt.stmt import *
from typing import List
from expr.visitor import AstPrinter

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0

    def parse(self) -> List[Stmt]:
        statements: List[Stmt] = []
        
        while not self.is_at_end():
            statements.append(self.declaration())

        return statements

    
    def declaration(self):
        if self.match(TokenType.VAR): return self.var_declaration()
        return self.statement()

    def var_declaration(self):
        name = self.consume(TokenType.IDENTIFIER, "Expect variable name")

        initializer = None
        if self.match(TokenType.EQUAL): 
            initializer = self.expression()

        self.consume(TokenType.SEMICOLON, "Expect ; variable declaration")
        return Var(name, initializer)

    def statement(self):
        if self.match(TokenType.PRINT): return self.print_statement()
        return self.expression_statement()

    def print_statement(self):
        value = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return Print(value)

    def expression_statement(self):
        value = self.expression()
        self.consume(TokenType.SEMICOLON, f"Expect ';' after expression.")
        return Expression(value)

    def expression(self) -> Expr:
        return self.conditional()

    def conditional(self) -> Conditional:
        expr = self.comma()

        if self.match(TokenType.QUESTION):
            then_branch = self.expression()
            self.consume(TokenType.COLON, "Expected : after expression.")
            else_branch = self.conditional()

            expr = Conditional(expr, then_branch, else_branch)
        
        return expr


    def comma(self) -> Binary:
        expr = self.assignment()

        if self.match(TokenType.COMMA):
            operator = self.previous()
            right = self.comma()
            expr = Binary(expr, operator, right)

        return expr

    def assignment(self) -> Assign:
        expr = self.equality()

        if self.match(TokenType.EQUAL):
            equals = self.previous()
            value = self.assignment()

            if isinstance(expr, Variable):
                return Assign(expr.name, value)
            
            Error.error(equals, "Invalid assignment target.")

        return expr

    def equality(self) -> Binary:
        expr = self.comparaison()
        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparaison()
            expr = Binary(expr, operator, right)

        return expr

    def comparaison(self) -> Binary:
        expr  = self.term()
        while self.match(TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL):
            operator = self.previous()
            right = self.term()
            expr = Binary(expr, operator, right)

        return expr

    def term(self) -> Binary | Unary:
        expr = self.factor()

        while self.match(TokenType.MINUS, TokenType.PLUS):
            operator = self.previous()
            right = self.factor()

            expr = Binary(expr, operator, right)
        
        return expr

    def factor(self) -> Unary | Binary:
        expr = self.unary()

        while self.match(TokenType.SLASH, TokenType.STAR):
            operator = self.previous()
            right = self.unary()

            expr = Binary(expr, operator, right)

        return expr

    def unary(self) -> Unary | Literal:
        if self.match(TokenType.BANG, TokenType.MINUS):
            operator = self.previous()
            right = self.unary()
            return Unary(operator, right)

        return self.primary()

    def primary(self) -> Literal | Grouping:
        if self.match(TokenType.TRUE): return Literal(True)
        if self.match(TokenType.FALSE): return Literal(False)
        if self.match(TokenType.NIL): return Literal(None)

        if self.match(TokenType.NUMBER, TokenType.STRING):
            return Literal(self.previous().literal)

        if self.match(TokenType.IDENTIFIER):
            return Variable(self.previous())

        if self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return Grouping(expr)
        
    def consume(self, type_, message):
        if self.check(type_): return self.advance()
        raise self.error(self.previous(), message)

    def match(self, *types):
        for type_ in types:
            if (self.check(type_)):
                self.advance()
                return True
        return False

    def check(self, type_):
        if self.is_at_end(): return False
        return self.peek().type == type_

    def advance(self):
        if not self.is_at_end(): self.current += 1
        return self.previous()

    def previous(self):
        return self.tokens[self.current-1]

    def peek(self):
        return self.tokens[self.current]
    
    def is_at_end(self):
        return self.peek().type == TokenType.EOF

    def error(self, token, message):
        Error.token_error(token, message)
        return ParseError()


class ParseError(RuntimeError):
    pass