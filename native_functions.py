from lox_callable import LoxCallable
from time import time

class LoxClock(LoxCallable):
    def arity(self): return 0
    def call(self, interpreter, arguments): return time()
    def __str__(self): return "<native_fun>"    


class LoxPrint(LoxCallable):
    def arity(self): return 1
    def call(self, interpreter, arguments):
        print(interpreter.stringify(arguments[0]))
    def __str__(self): return "<native_fun>"