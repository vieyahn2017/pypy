# -*- coding: utf-8 -*- 

import ast
# Python AST (Abstract Syntax Tree)


expr = """
def add(arg1, arg2):
    return arg1 + arg2
"""

expr_ast = ast.parse(expr)

ast.dump(expr_ast)

class CrazyTransformer(ast.NodeTransformer):
    def visit_BinOp(self, node):
        print node.__dict__
        node.op = ast.Mult()
        print node.__dict__
        return node

transformer = CrazyTransformer()
transformer.visit(expr_ast)

unmodified = ast.parse(expr)
exec compile(unmodified, '<string>', 'exec')
print add(4, 5) #9

transformer = CrazyTransformer()
modified = transformer.visit(unmodified)
exec compile(modified, '<string>', 'exec')
print add(4, 5) #20




Num = lambda env, n: n  
Var = lambda env, x: env[x]  
Add = lambda env, a, b:_eval(env, a) + _eval(env, b)  
Mul = lambda env, a, b:_eval(env, a) * _eval(env, b)  
  
_eval = lambda env, expr:expr[0](env, *expr[1:])  
  
env = {'a':2, 'b':5}  
tree = (Add, (Var, 'a'),  
             (Mul, (Num, 3),  
                   (Var, 'b')))  
print _eval(env, tree)  # 17

