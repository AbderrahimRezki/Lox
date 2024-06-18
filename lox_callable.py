from abc import ABC, abstractmethod

class LoxCallable(ABC):
    @abstractmethod
    def call(self, interpreter, arguments): pass

    @abstractmethod
    def arity(self) -> int: pass

