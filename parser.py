from lox_token import Token, TokenType
from errors import Error
from expr import *
from stmt import *
from typing import List
from printer import AstPrinter

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
        if self.match(TokenType.FUN): return self.fun_declaration()
        return self.statement()

    def var_declaration(self):
        name = self.consume(TokenType.IDENTIFIER, "Expect variable name")

        initializer = None
        if self.match(TokenType.EQUAL): 
            initializer = self.expression()

        self.consume(TokenType.SEMICOLON, "Expect ; after variable declaration")
        return Var(name, initializer)

    def fun_declaration(self):
        return self.function()

    def function(self, kind="function"):
        name = self.consume(TokenType.IDENTIFIER, f"Expect {kind} name.")
        self.consume(TokenType.LEFT_PAREN, f"Expect '(' after {kind} name.")

        parameters: List[Token] = []

        if not self.check(TokenType.RIGHT_PAREN):
            parameters.append(self.consume(TokenType.IDENTIFIER, "Expect parameter name."))

            while self.match(TokenType.COMMA):
                if len(parameters) >= 255:
                    self.error(self.peek(), "Can't have more than 255 parameters.")

                parameters.append(self.consume(TokenType.IDENTIFIER, "Expect parameter name."))

        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after parameters.")
        self.consume(TokenType.LEFT_BRACE, f"Expect '{{' before {kind} body.")
        
        body = self.block_statement()

        return Function(name, parameters, body)

    def statement(self):
        if self.match(TokenType.IF): return self.if_statement()
        if self.match(TokenType.FOR): return self.for_statement()
        if self.match(TokenType.PRINT): return self.print_statement()
        if self.match(TokenType.WHILE): return self.while_statement()
        if self.match(TokenType.LEFT_BRACE): return Block(self.block_statement())
        return self.expression_statement()

    def if_statement(self):
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after if.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after if condition.")
        then_branch = self.statement()
        else_branch = None
        if self.match(TokenType.ELSE):
            else_branch = self.statement()

        return If(condition, then_branch, else_branch)

    def for_statement(self):
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after for.")
        
        if self.match(TokenType.SEMICOLON):
            initializer = None
        elif self.match(TokenType.VAR):
            initializer = self.var_declaration()
        else:
            initializer = self.expression_statement()

        condition = Literal(True)
        if not self.check(TokenType.SEMICOLON):
            condition = self.expression()

        self.consume(TokenType.SEMICOLON, "Expect ';' after for condition.")

        increment = None
        if not self.check(TokenType.SEMICOLON):
            increment = self.expression()

        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after for clauses.")

        body = self.statement()

        if increment is not None:
            body = Block(statements=[
                body,
                increment
            ])

        body = While(condition, body)

        if initializer is not None:
            body = Block(statements=[
                initializer, 
                body
            ])

        return body


    def print_statement(self):
        value = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return Print(value)

    def while_statement(self):
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after while.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after while condition.")

        body = self.statement()

        return While(condition, body)

    def block_statement(self):
        statements: List[Stmt] = []

        while not self.is_at_end() and not self.check(TokenType.RIGHT_BRACE):
            statements.append(self.declaration())

        self.consume(TokenType.RIGHT_BRACE, "Expect '}' at the end of block.")
        return statements

    def expression_statement(self):
        value = self.expression()
        self.consume(TokenType.SEMICOLON, f"Expect ';' after expression.")
        return Expression(value)

    def expression(self) -> Expr:
        return self.conditional()

    def conditional(self) -> Conditional:
        expr = self.assignment()

        if self.match(TokenType.QUESTION):
            then_branch = self.expression()
            self.consume(TokenType.COLON, "Expected ':' after expression.")
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
        expr = self.logical_or()

        if self.match(TokenType.EQUAL):
            equals = self.previous()
            value = self.assignment()

            if isinstance(expr, Variable):
                return Assign(expr.name, value)
            
            Error.error(equals, "Invalid assignment target.")

        return expr

    def logical_or(self) -> Binary:
        expr = self.logical_and()

        while self.match(TokenType.OR) and not self.is_at_end():
            operator = self.previous()
            right = self.logical_and()

            if right is None:
                Error.error(operator, f"Expect expression after or, got <{right}>.")
            expr = Logical(expr, operator, right)

        return expr

    def logical_and(self) -> Binary:
        expr = self.equality()

        while self.match(TokenType.AND) and not self.is_at_end():
            operator = self.previous()
            right = self.equality()
            expr = Logical(expr, operator, right)

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

        return self.call()

    def call(self):
        expr = self.primary()

        while True:
            if self.match(TokenType.LEFT_PAREN):
                expr = self.finish_call(expr)
            else: break

        return expr

    def finish_call(self, expr):
        arguments = []
        if not self.check(TokenType.RIGHT_PAREN):
            arguments.append(self.assignment())

            while self.match(TokenType.COMMA):
                if len(arguments) >= 255:
                    self.error(self.peek(), "Can't have more than 255 arguments")
                arguments.append(self.expression())

        paren = self.consume(TokenType.RIGHT_PAREN, "Expect ')' after arguments")
        return Call(expr, paren, arguments)

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