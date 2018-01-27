# -*- coding: utf-8 -*- 

import ast
import parser


def process(node):

    if isinstance(node, ast.Num):
        return str(node.n)
    elif isinstance(node, ast.Name):
        return node.id
    elif isinstance(node, ast.Str):
        return r"\b%s\b" % node.s
    elif isinstance(node, ast.Expr):
        return process(node.value)
    elif isinstance(node, ast.BinOp):
        # It's a binary op so we recursively call the binary op methods.
        if isinstance(node.op, ast.Mult):
            return and_(process(node.left), process(node.right))
        elif isinstance(node.op, ast.Add):
            return or_(process(node.left), process(node.right))
    elif isinstance(node, ast.UnaryOp):
        # This is actually negations.
        operand = node.operand
        if isinstance(operand, ast.Name):
            return negate(operand.id)
        elif isinstance(operand, ast.Str):
            return negate(operand.s)
        elif isinstance(operand, ast.Num):
            return negate(operand.n)

def create_rule(rule, ignore_case=False):
    """ 
    Use Python's AST parser to generate a tree which we'll traverse to create a
    regular expression.
    """
    results = parser.tokens(rule.strip())
    ast_string = ''

    unicode_strings = []
    
    for token in results:
        if token.type == 'OR':
            ast_string += '+' 
        elif token.type == 'AND':
            ast_string += '*' 
        else:
            try:
                ast_string += token.value.decode('ascii')
            except:
                ast_string += 'PLACEHOLDER%s' % len(unicode_strings)
                unicode_strings.append(token.value)
    
    tree = ast.parse(ast_string)
    root = tree.body[0]
    regexp = process(root)

    # Check if we have to replace any strings.
    for idx, u in enumerate(unicode_strings):
        regexp = regexp.replace('PLACEHOLDER%s' % idx, u)

    if ignore_case:
        return re.compile(regexp, re.IGNORECASE)
    else:
        return re.compile(regexp)


# 用Python的AST模块解析文本 [复制链接] 制定规则。。。
# Photography: photo OR camera OR picture
# Photoshop: "Photoshop" -photo -shop

# Photograph: 'photo|camera|picture'
# Photoshop: '(?=.*(?=.*\\bPhotoshop\\b).*^((?!photo).)*$).*^((?!shop).)*$'

create_rule('photo|camera|picture')