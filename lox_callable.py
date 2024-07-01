from abc import ABC, abstractmethod
from stmt import Function
from typing import List
from lox_token import Token
from environment import Environment

class LoxCallable(ABC):
    @abstractmethod
    def call(self, interpreter, arguments): pass

    @abstractmethod
    def arity(self) -> int: pass


class LoxFunction(LoxCallable):
    def __init__(self, declaration: Function):
        self.declaration = declaration

    def call(self, interpreter, arguments: List):
        self.environment = Environment(interpreter.globals)

        for parameter, argument in zip(self.declaration.parameters, arguments):
            self.environment.define(parameter, argument)

        interpreter.execute_block(self.declaration.body, self.environment)

    def arity(self): return len(self.declaration.parameters)

    def __str__(self): return f"<fun {self.declaration.name.lexeme}>"