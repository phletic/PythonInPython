
class NumberNode:
    def __init__(self, tok):
        self.tok = tok

    def __repr__(self):
        return f'{self.tok}'


class VarAcessNode:
    def __init__(self, var_name):
        self.var_name = var_name

    def __repr__(self):
        return f"g:{self.var_name}"


class VarAssignNode:
    def __init__(self, var_name, value_node):
        self.name = var_name
        self.value_node = value_node

    def __repr__(self):
        return f'({self.name},{self.value_node})'

class NullNode:
    def __repr__(self):
        return f"NULL"

class BinOpNode:
    def __init__(self, left_node, op_tok, right_node):
        self.left_node = left_node
        self.op_tok = op_tok
        self.right_node = right_node

    def __repr__(self):
        return f'({self.left_node}, {self.op_tok}, {self.right_node})'


class variableOpNode:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def __repr__(self):
        return f'({self.left}, {self.op}, {self.right})'


class UnaryOpNode:
    def __init__(self, op, node):
        self.op = op
        self.node = node

    def __repr__(self):
        return f'({self.op},{self.node})'


class BoolNode:
    def __init__(self, tok):
        self.tok = tok

    def __repr__(self):
        return f'{self.tok}'


class IfLoopNode:
    def __init__(self, cases, elseCase):
        self.cases = cases
        self.elseCase = elseCase

    def __repr__(self):
        return str(list(self.cases))


class WhileNode:
    def __init__(self, condition, expresion):
        self.condition = condition
        self.expression = expresion

    def __repr__(self):
        return f"(w:{self.condition}/{self.expression})"


class ForLoop:
    def __init__(self, assignment, condition, increment, expression):
        self.assignment = assignment
        self.condition = condition
        self.increment = increment
        self.expression = expression

    def __repr__(self):
        return f"({self.assignment};{self.condition};{self.increment};{self.expression})"

class FunctionNode:
    def __init__(self,name,arguments,expression):
        self.name = name.val if name != None else "anonymous"
        self.arguments = arguments
        self.expression = expression
    def __repr__(self):
        return f"(func <{self.name}> {self.arguments}, {self.expression})"

class callFunctionNode:
    def __init__(self,name,arguments):
        self.name = name
        self.arguments = arguments
    def __repr__(self):
        return f"(Cfunc <{self.name}> {self.arguments} )"

class StringNode:
    def __init__(self,val):
        self.val = val
    def __repr__(self):
        return f"str:{self.val}"