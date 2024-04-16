import sys
from lox_token import Token, TokenType

class LoxRuntimeError(RuntimeError):
    def __init__(self, token: Token, message):
        super().__init__(message)
        self.token = token

class Error:
    had_error = False
    had_runtime_error = False

    @staticmethod
    def error(line, message):
        Error.report(line, "", message)

    @staticmethod
    def report(line, where, message):
        sys.stderr.write(f"[{line}] Error {where}: {message}\n")
        Error.had_error = True

    @staticmethod
    def token_error(token: Token, message):
        if token.type == TokenType.EOF:
            Error.report(token.line, " at end", message)
        else:
            Error.report(token.line, f" at '{token.lexeme}'", message)

    @staticmethod
    def runtime_error(error: LoxRuntimeError):
        msg = ""
        if hasattr(LoxRuntimeError, "message"):
            msg = error.message
        else:
            msg = error

        sys.stderr.write(f"[line {error.token.line}] {msg}\n")
        Error.had_runtime_error = True