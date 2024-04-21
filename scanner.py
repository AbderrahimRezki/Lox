from lox_token import Token, TokenType
from errors import Error
from typing import List

class Scanner:
    def __init__(self, source):
        self.start = 0
        self.current = 0
        self.line = 1
        self.source = source
        self.tokens: List[Token] = []
        self.keywords = {
            "and": TokenType.AND,
            "or": TokenType.OR,
            "class": TokenType.CLASS,
            "else": TokenType.ELSE,
            "false": TokenType.FALSE,
            "for": TokenType.FOR,
            "fun": TokenType.FUN,
            "if": TokenType.IF,
            "nil": TokenType.NIL,
            "or": TokenType.OR,
            "print": TokenType.PRINT,
            "return": TokenType.RETURN,
            "super": TokenType.SUPER,
            "this": TokenType.THIS,
            "true": TokenType.TRUE,
            "var": TokenType.VAR,
            "while": TokenType.WHILE,
        }

    def scan_tokens(self):
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()

        self.tokens.append(Token(TokenType.EOF, '', None, self.line))
        return self.tokens

    def scan_token(self):
        c = self.advance()
        match(c):
            case x if x in [' ', '\r', '\t']: pass
            case '\n': self.line += 1
            case '(': self.add_token(TokenType.LEFT_PAREN)
            case ')': self.add_token(TokenType.RIGHT_PAREN)
            case '{': self.add_token(TokenType.LEFT_BRACE)
            case '}': self.add_token(TokenType.RIGHT_BRACE)
            case '+': self.add_token(TokenType.PLUS)
            case '-': self.add_token(TokenType.MINUS)
            case '*': self.add_token(TokenType.STAR)
            case ':': self.add_token(TokenType.COLON)
            case ';': self.add_token(TokenType.SEMICOLON)
            case ',': self.add_token(TokenType.COMMA)
            case '.': self.add_token(TokenType.DOT)
            case '?': self.add_token(TokenType.QUESTION)
            case '!': self.add_token(TokenType.BANG_EQUAL if self.match('=') else TokenType.BANG)
            case '=': self.add_token(TokenType.EQUAL_EQUAL if self.match('=') else TokenType.EQUAL)
            case '<': self.add_token(TokenType.LESS_EQUAL if self.match('=') else TokenType.LESS)
            case '>': self.add_token(TokenType.GREATER_EQUAL if self.match('=') else TokenType.GREATER)
            case '/':
                if self.match('/'):
                    while self.peek() != '\n' and not self.is_at_end():
                        self.advance()
                elif self.match("*"): self.multiline_comment()
                else:
                    self.add_token(TokenType.SLASH)
            case '"': self.string()
            case _:
                if c.isnumeric(): self.number()
                elif self.is_alpha(c): self.identifier()
                else: Error.error(self.line, f'Unexpected character <{c}>')

    def identifier(self):
        while self.is_alphanumeric(self.peek()): self.advance()
        text = self.source[self.start:self.current]

        token_type = self.keywords.get(text)

        if token_type is None: self.add_token(TokenType.IDENTIFIER)
        else: self.add_token(token_type)

    def number(self):
        while self.peek().isnumeric(): self.advance()
        if self.peek() == "." and self.peek_next().isnumeric(): self.advance()
        while self.peek().isnumeric(): self.advance()

        value = float(self.source[self.start:self.current])
        self.add_token_(TokenType.NUMBER, value)
    
    def string(self):
        while self.peek() != '"' and not self.is_at_end():
            if self.peek() == "\n": self.line += 1
            self.advance()

        if self.is_at_end(): 
            Error.error(self.line, "Unterminated string.")
            return
        
        self.advance()
        value = self.source[self.start + 1:self.current - 1]
        self.add_token_(TokenType.STRING, value)

    def multiline_comment(self):
        count = 1
        while count > 0 and not self.is_at_end():
            if self.peek() == "/" and self.peek_next() == "*":
                count += 1
                self.advance()
                self.advance()
                continue

            if self.peek() == "*" and self.peek_next() == "/":
                count -= 1
                self.advance()
                self.advance()
                continue

            if self.peek() == "\n": self.line += 1
            self.advance()

        if self.is_at_end() and count > 0: 
            Error.error(self.line, "Unterminated multi-line comment.")

    def match(self, expected):
        if self.is_at_end(): return False
        if self.source[self.current] != expected: return False
        self.current += 1
        return True

    def peek(self):
        if self.is_at_end(): return '\0'
        return self.source[self.current]

    def peek_next(self):
        if self.current + 1 >= len(self.source): return '\0'
        return self.source[self.current+1]

    def is_alpha(self, char):
        return char.isalpha() or char == "_"

    def is_alphanumeric(self, char):
        return char.isnumeric() or self.is_alpha(char)

    def is_at_end(self):
        return self.current >= len(self.source)

    def advance(self):
        self.current += 1
        return self.source[self.current - 1]

    def add_token(self, token_type):
        self.add_token_(token_type, None)

    def add_token_(self, token_type, literal):
        text = self.source[self.start:self.current]
        self.tokens.append(Token(token_type, text, literal, self.line))

    