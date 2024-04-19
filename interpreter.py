from expr import *
from stmt import *
from environment import EnvironmentSingleton
from lox_token import Token, TokenType
from errors import Error, LoxRuntimeError
from typing import List
import sys

# TODO: support nested assignment

class Interpreter(StmtVisitor, ExprVisitor):
    def __init__(self):
        self.environment = EnvironmentSingleton.get_env()

    def visit_expression_stmt(self, stmt: Expression):
        self.eval(stmt.expression)

    def visit_print_stmt(self, stmt: Print):
        value = self.stringify(self.eval(stmt.expression))
        sys.stdout.write(value + "\n")

    def visit_declaration_stmt(self, stmt: Var):
        value = None

        if stmt.initializer is not None:
            value = self.eval(stmt.initializer)

        self.environment.define(stmt.name, value)

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

    def visit_conditional_expr(self, expr: Conditional):
        condition = self.eval(expr.condition)

        if self.is_truthy(condition):
            return self.eval(expr.then_branch)

        return self.eval(expr.else_branch)
    
    def visit_grouping_expr(self, expr: Grouping): 
        return self.eval(expr.expression)

    def visit_literal_expr(self, expr: Literal): 
        return expr.value

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