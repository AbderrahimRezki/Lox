from lox_token import Token
from errors import LoxRuntimeError
from extensions import LoxLoggerSingleton


class Environment:
    def __init__(self):
        self.__values = dict()

    def get(self, name: Token) -> object:
        obj = self.__values.get(name.lexeme, None)

        LoxLoggerSingleton.get_logger().log(3, msg = f"[GET] var {name.lexeme} = {obj}")

        if obj is not None: 
            return obj

        raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")

    def define(self, name: Token, value: object):
        self.__values[name.lexeme] = value

        LoxLoggerSingleton.get_logger().log(3, msg=f"[DEFINE] var {name.lexeme} = {value}")

    def assign(self, name: Token, value: object) -> object:
        if name.lexeme in self.__values:
            self.__values[name.lexeme] = value

            LoxLoggerSingleton.get_logger().log(3, msg=f"[ASSIGN] {name.lexeme} = {value}")
            return value

        raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")

class EnvironmentSingleton:
    env = None

    @classmethod
    def get_env(cls):
        if cls.env is None:
            cls.env = Environment()
        return cls.env