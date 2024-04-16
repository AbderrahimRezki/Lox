from dataclasses import dataclass
from enum import Enum, auto

class TokenType(Enum):
    # One character tokens
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    LEFT_BRACE = auto()
    RIGHT_BRACE      = auto()
    COMMA = auto()
    DOT = auto()
    MINUS = auto()
    PLUS = auto()
    COLON = auto()
    SEMICOLON = auto()
    SLASH = auto()
    STAR = auto()
    QUESTION = auto()

    # One or two character tokens
    BANG = auto()
    BANG_EQUAL = auto()
    EQUAL = auto()
    EQUAL_EQUAL = auto()
    GREATER = auto()
    GREATER_EQUAL = auto()
    LESS = auto()
    LESS_EQUAL = auto()

    # Literals
    IDENTIFIER = auto()
    STRING = auto()
    NUMBER = auto()

    # Keywords
    AND = auto()
    CLASS = auto()
    ELSE = auto()
    FALSE = auto()
    FUN = auto()
    FOR = auto()
    IF = auto()
    NIL = auto()
    OR = auto()
    PRINT = auto()
    RETURN = auto()
    SUPER = auto()
    THIS = auto()
    TRUE = auto()
    VAR = auto()
    WHILE = auto()
    EOF = auto()


@dataclass
class Token:
    type: TokenType
    lexeme: str
    literal: str | float
    line: int

    def __str__(self):
        return f"{self.type} {self.lexeme} {self.literal}"