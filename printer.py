from expr import *

class AstPrinter(ExprVisitor):
    def visit_conditional_expr(self, expr: Conditional):
        return self.parenthesize("condition", expr.condition, expr.then_branch, expr.else_branch)

    def visit_binary_expr(self, expr: Binary):
        return self.parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visit_grouping_expr(self, expr: Grouping): 
        return self.parenthesize("group", expr.expression)
    
    def visit_literal_expr(self, expr: Literal): 
        return expr.value if expr.value is not None else "nil"

    def visit_unary_expr(self, expr: Unary):
        return self.parenthesize(expr.operator.lexeme, expr.right)
   
    def parenthesize(self, name, *exprs):
        out = f"( {name}"
        for expr in exprs:
            out += " "
            out += str(expr.accept(self))
        out += ")"
        return  out

    def print(self, expr):
        if isinstance(expr, Expr):
            return expr.accept(self)
        print("Not an expresssion")