from lox_token import Token
from errors import LoxRuntimeError

class Environment:
    def __init__(self, enclosing = None):
        self.__enclosing = enclosing
        self.__values = dict()

    def get(self, name: Token) -> object:
        if name.lexeme in self.__values:
            return self.__values[name.lexeme]

        if self.__enclosing is not None:
            return self.__enclosing.get(name)

        raise LoxRuntimeError(name, 
            f"Undefined variable '{name.lexeme}'.")

    def define(self, name: Token, value: object):
        self.__values[name.lexeme] = value

    def assign(self, name: Token, value: object) -> object:
        if name.lexeme in self.__values:
            self.__values[name.lexeme] = value
            return value

        if self.__enclosing is not None:
            return self.__enclosing.assign(name, value)

        raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")

class EnvironmentSingleton:
    env = None

    @classmethod
    def get_env(cls):
        if cls.env is None:
            cls.env = Environment()
        return cls.env