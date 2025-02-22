from expr import *
from stmt import *
from environment import EnvironmentSingleton, Environment
from lox_token import Token, TokenType
from lox_callable import LoxCallable, LoxFunction
from native_functions import LoxClock, LoxPrint
from errors import Error, LoxRuntimeError
from typing import List
import sys

from printer import AstPrinter

class Interpreter(StmtVisitor, ExprVisitor):
    def __init__(self):
        self.globals: Environment = EnvironmentSingleton.get_env()
        self.environment: Environment = self.globals

        self.globals.define(Token(TokenType.IDENTIFIER, "clock", None, 0), LoxClock())
        self.globals.define(Token(TokenType.IDENTIFIER, "printf", None, 0), LoxPrint())

    def visit_expression_stmt(self, stmt: Expression):
        self.eval(stmt.expression)

    def visit_function_stmt(self, stmt: Function):
        function = LoxFunction(stmt)
        self.environment.define(stmt.name, function)

    def visit_if_stmt(self, stmt: If):
        if self.is_truthy(self.eval(stmt.condition)):
            self.execute(stmt.then_branch)
        elif stmt.else_branch is not None:
            self.execute(stmt.else_branch)

    def visit_print_stmt(self, stmt: Print):
        value = self.stringify(self.eval(stmt.expression))
        sys.stdout.write(value + "\n")

    def visit_block_stmt(self, stmt: Block):
        self.execute_block(stmt.statements, Environment(self.environment))

    def visit_declaration_stmt(self, stmt: Var):
        value = None

        if stmt.initializer is not None:
            value = self.eval(stmt.initializer)

        self.environment.define(stmt.name, value)

    def visit_while_stmt(self, stmt: While):
        while self.is_truthy(self.eval(stmt.condition)):
            self.execute(stmt.body)

    def visit_binary_expr(self, expr: Binary): 
        left = self.eval(expr.left)
        right = self.eval(expr.right)
        operator = expr.operator

        match(operator.type):
            case TokenType.PLUS:    
                if (isinstance(left, float) and isinstance(right, float))   \
                    or (isinstance(left, str) and isinstance(right, str)):   
                    return left + right
                elif (isinstance(left, str) or isinstance(right, str)):
                    return str(left) + str(right)
                raise LoxRuntimeError(operator, 
                    f"Not supported between operands of type {type(left)} and {type(right)}.")
            
            case TokenType.MINUS:           
                self.check_number_operands(operator, left, right)
                return left - right

            case TokenType.STAR:            
                self.check_number_operands(operator, left, right)
                return left * right

            case TokenType.SLASH:           
                self.check_number_operands(operator, left, right)
                if right == 0:
                    raise LoxRuntimeError(operator, "Division by Zero")
                return left / right

            case TokenType.COMMA:           
                return right

            case TokenType.EQUAL_EQUAL:    
                return left == right

            case TokenType.BANG_EQUAL:     
                return left != right

            case TokenType.LESS:            
                self.check_number_operands(operator, left, right)
                return left < right

            case TokenType.LESS_EQUAL:      
                self.check_number_operands(operator, left, right)
                return left <= right

            case TokenType.GREATER:         
                self.check_number_operands(operator, left, right)
                return left > right

            case TokenType.GREATER_EQUAL:   
                self.check_number_operands(operator, left, right)
                return left >= right

            case _:                         
               raise NotImplementedError(f"Operator type <{operator.type}> not implemented.") 

    def visit_call_expr(self, expr: Call):
        callee: LoxCallable = self.eval(expr.callee)

        if not isinstance(callee, LoxCallable):
            raise LoxRuntimeError(expr.paren, "Can only call functions and classes")

        arguments = []

        for arg in expr.arguments:
            arguments.append(self.eval(arg))

        if len(arguments) != callee.arity():
            raise LoxRuntimeError(expr.paren, f"Expected {callee.arity()} args but got {len(arguments)}.")

        return callee.call(self, arguments)

    def visit_conditional_expr(self, expr: Conditional):
        condition = self.eval(expr.condition)

        if self.is_truthy(condition):
            return self.eval(expr.then_branch)

        return self.eval(expr.else_branch)
    
    def visit_grouping_expr(self, expr: Grouping): 
        return self.eval(expr.expression)

    def visit_literal_expr(self, expr: Literal): 
        return expr.value

    def visit_logical_expr(self, expr: Logical):
        left = self.is_truthy(self.eval(expr.left))
        operator = expr.operator

        if operator.type == TokenType.OR: 
            if left == True: return True
        elif operator.type == TokenType.AND:
            if left == False: return False

        return self.eval(expr.right)

    def visit_unary_expr(self, expr: Unary): 
        right = self.eval(expr.right)

        match(expr.operator.type):
            case TokenType.BANG:
                return not self.is_truthy(right)

            case TokenType.MINUS:
                self.check_number_operand(expr.operator, right)
                return -right

            case _:
                raise NotImplementedError(f"Operator <{expr.operator.type}> not implemented.")

    def visit_variable_expr(self, expr: Variable):
        return self.environment.get(expr.name)

    def visit_assign_expr(self, expr: Assign):
        value = self.eval(expr.value)
        self.environment.assign(expr.name, value)
        return value 

    def check_number_operand(self, operator: Token, operand):
        if not isinstance(operand, float):
            raise LoxRuntimeError(operator, "Operand must be a number")

    def check_number_operands(self, operator: Token, left, right):
        if not (isinstance(left, float) and isinstance(right, float)):
            raise LoxRuntimeError(operator, "Operands must be numbers")

    def is_truthy(self, obj):
        # Keeping python's truthiness
        return not not obj

    def stringify(self, value):
        if value is None: return "nil"
        if isinstance(value, bool): return str(value).lower()

        if isinstance(value, float):
            value_as_str = str(value)
            if value_as_str.endswith(".0"):
                return value_as_str[:-2]

        return str(value)

    def eval(self, expr: Expr):
        return expr.accept(self)

    def interpret(self, statements: List[Stmt]):
        try:
            for statement in statements:
                self.execute(statement)
        except LoxRuntimeError as e:
            Error.runtime_error(e)

    def execute(self, stmt: Stmt):
        stmt.accept(self)

    def execute_block(self, statements: List[Stmt], environment: Environment):
        previous = self.environment

        try:
            self.environment = environment

            for statement in statements:
                self.execute(stmt=statement)

        finally:
            self.environment = previous