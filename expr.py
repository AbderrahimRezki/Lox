from abc import ABC, abstractmethod
from lox_token import Token
from typing import List

class ExprVisitor(ABC):
	@abstractmethod
	def visit_conditional_expr(self, expr): pass
	
	@abstractmethod
	def visit_binary_expr(self, expr): pass 

	@abstractmethod  
	def visit_grouping_expr(self, expr): pass

	@abstractmethod
	def visit_literal_expr(self, expr): pass

	@abstractmethod
	def visit_logical_expr(self, expr): pass

	@abstractmethod
	def visit_unary_expr(self, expr): pass
	
	@abstractmethod
	def visit_variable_expr(self, name): pass

	@abstractmethod
	def visit_assign_expr(self, name): pass


class Expr:
	def accept(self, visitor: ExprVisitor) -> object: pass


class Conditional(Expr):
	def __init__(self, condition: Expr, then_branch: Expr, else_branch: Expr):
		self.condition = condition
		self.then_branch = then_branch
		self.else_branch = else_branch

	def accept(self, visitor: ExprVisitor):
		return visitor.visit_conditional_expr(self)

class Binary(Expr):
	def __init__(self, left: Expr, operator: Token, right: Expr):
		self.left = left
		self.operator = operator
		self.right = right

	def accept(self, visitor: ExprVisitor):
		return visitor.visit_binary_expr(self)

class Call(Expr):
	def __init__(self, callee: Expr, paren: Token, arguments: List[Expr]): 
		self.callee = callee
		self.paren = paren
		self.arguments = arguments

	def accept(self, visitor: ExprVisitor):
		return visitor.visit_call_expr(self)

class Grouping(Expr):
	def __init__(self, expression: Expr):
		self.expression = expression

	def accept(self, visitor: ExprVisitor):
		return visitor.visit_grouping_expr(self)

class Literal(Expr):
	def __init__(self, value):
		self.value = value

	def accept(self, visitor: ExprVisitor):
		return visitor.visit_literal_expr(self)	

class Logical(Expr):
	def __init__(self, left: Expr, operator: Token, right: Expr):
		self.left = left
		self.operator = operator
		self.right = right

	def accept(self, visitor: ExprVisitor):
		return visitor.visit_logical_expr(self)

class Unary(Expr):
	def __init__(self, operator: Token, right: Expr):
		self.operator = operator
		self.right = right
	
	def accept(self, visitor: ExprVisitor):
		return visitor.visit_unary_expr(self)

class Variable(Expr):
	def __init__(self, name: Token):
		self.name = name

	def accept(self, visitor: ExprVisitor):
		return visitor.visit_variable_expr(self)


class Assign(Expr):
	def __init__(self, name: Token, value: Expr):
		self.name = name
		self.value = value
	
	def accept(self, visitor: ExprVisitor):
		return visitor.visit_assign_expr(self)