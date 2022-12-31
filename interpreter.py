from dataTypes import Number, _Bool, TT_OP, VARIABLEOP,NULL,Function,TT_identifier,String
from symbolTable import SymbolTable
from Error import RTError,StackOverflow
from ParserNodes import VarAssignNode
from lexerAnalysis import Token

def writeLine(text):
    print(text,end='\n')


class RTResult:
    def __init__(self):
        self.value = None
        self.error = None

    def register(self, res):
        if res.error:
            self.error = res.error
        return res.value

    def sucess(self, res):
        self.value = res
        return self

    def failure(self, res):
        self.error = res
        return self


class Interpreter:
    def __init__(self, symbolTable):
        self.symbolTable = symbolTable
        self.output = None

    def visit(self, node):
        methodName = f"visit_{type(node).__name__}"
        method = getattr(self, methodName, self.no_visit)
        return method(node)

    def no_visit(self, node):
        raise Exception(f"{type(node).__name__} is not impliemented")

    def visit_NullNode(self,Node):
        res = RTResult()
        return res.sucess(NULL(True))

    def visit_StringNode(self, Node):
        res = RTResult()
        string =  Node.val.val
        return res.sucess(String(string))

    # todo : variable declared must be local
    def visit_WhileNode(self, node):
        res = RTResult()
        localSymbolTable = SymbolTable()
        localSymbolTable.addParent(self.symbolTable)
        self.symbolTable = localSymbolTable
        condition = res.register(self.visit(node.condition))
        expression = node.expression
        if res.error: return res
        while condition.val == 1:
            expressionResult = res.register(self.visit(expression))
            if res.error: return res
            if expressionResult != None:
                writeLine(expressionResult)
            condition = res.register(self.visit(node.condition))
        self.symbolTable = self.symbolTable.parent
        return res.sucess(None)

    def visit_IfLoopNode(self, node):
        res = RTResult()
        for test, expr in node.cases:
            validity = res.register(self.visit(test))
            if res.error: return res
            if validity.val == _Bool("TRUE").val:
                expressionVal = res.register(self.visit(expr))
                if res.error: return res
                return res.sucess(expressionVal)
        if node.elseCase != None:
            elseExp = res.register(self.visit(node.elseCase))
            if res.error: return res
            return res.sucess(elseExp)
        else:
            return res.sucess(NULL(False))

    def visit_NumberNode(self, node):
        res = RTResult()
        return res.sucess(Number(node.tok.val))

    def visit_BoolNode(self, node):
        res = RTResult()
        return res.sucess(_Bool(node.tok.val))

    # read local variables
    def visit_VarAcessNode(self, node):
        res = RTResult()
        var_name = node.var_name.val
        value = self.symbolTable.get(var_name)
        if not value:
            return res.failure(RTError(f"{var_name} is not defined"))
        else:
            return res.sucess(value)
    
    def visit_FunctionNode(self,node):
        res = RTResult()
        name = node.name
        arguments = node.arguments
        expression = node.expression
        if name == "anonymous":
            return res.sucess(Function(name,arguments,expression))
        self.symbolTable.set(name,Function(name,arguments,expression))
        return res.sucess(NULL(False))

    def visit_callFunctionNode(self,node):
        res = RTResult()
        localVariableNode = SymbolTable()
        localVariableNode.addParent(self.symbolTable)
        self.symbolTable = localVariableNode
        name = node.name
        arguments = node.arguments
        function = self.symbolTable.get(name.val)
        if function == None:
            return res.failure(RTError("Function does not exist"))
        Fexpression = function.expression
        Fargs = function.arguments
        if len(Fargs) > len(arguments):
            return res.failure(RTError("too few arguments given"))
        if len(Fargs) < len(arguments):
            return res.failure(RTError("too many arguments given"))
        for i,e in enumerate(Fargs):
            newVariableAssignNode = VarAssignNode(e,arguments[i])
            res.register(self.visit(newVariableAssignNode))
            if res.error: return res
        try:
            result = res.register(self.visit(Fexpression))
        except MemoryError:
            return res.failure(StackOverflow("function call stack too huge"))
        if res.error: return res
        else: return res.sucess(result)

    # write local variables
    def visit_VarAssignNode(self, node):
        res = RTResult()
        var_name = node.name.val
        value = res.register(self.visit(node.value_node))
        if isinstance(value,NULL):
            value.shouldRepresent = True
        if res.error:
            return res
        self.symbolTable.set(var_name, value)
        return res.sucess(value)

    def visit_BinOpNode(self, node):
        res = RTResult()
        left = res.register(self.visit(node.left_node))
        if res.error:
            return res
        right = res.register(self.visit(node.right_node))
        if res.error:
            return res
        methodName = TT_OP[node.op_tok.dataType.op].function    
        method = getattr(left, methodName, getattr(left, "noImp"))
        result, error = method(right)
        if error:
            return res.failure(error)
        return res.sucess(result)

    def visit_UnaryOpNode(self, node):
        res = RTResult()
        number = res.register(self.visit(node.node))
        result, error = number.negate(node.op.dataType)
        if error:
            return res.failure(error)
        else:
            return res.sucess(result)

    def visit_variableOpNode(self, node):
        res = RTResult()
        variable = res.register(self.visit(node.left))
        if res.error: return res
        value = res.register(self.visit(node.right))
        if res.error: return res
        methodName = VARIABLEOP[node.op.dataType.op].function
        method = getattr(variable, methodName, getattr(variable, "noImp"))
        result, error = method(value)
        if error:
            return res.failure(error)
        self.symbolTable.set(node.left.var_name.val, result)
        return res.sucess(None) 

    def visit_ForLoop(self,node):
        localVariableTree = SymbolTable()
        localVariableTree.addParent(self.symbolTable)
        self.symbolTable = localVariableTree
        assignment = node.assignment
        condition = node.condition
        increment = node.increment
        expression = node.expression
        res = RTResult()
        res.register(self.visit(assignment))
        conditionValidity = res.register(self.visit(condition))
        if res.error: return res
        while conditionValidity.val == 1:
            expressionResult = res.register(self.visit(expression))
            if res.error: return res
            if expressionResult != None:
                writeLine(expressionResult)
            res.register(self.visit(increment))
            conditionValidity = res.register(self.visit(condition))   
        self.symbolTable.revertToParent()
        return res.sucess(None)