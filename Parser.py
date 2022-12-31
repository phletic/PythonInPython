from lexerAnalysis import Token
from dataTypes import TT_NUM, TT_OP, EOF, max_precedence, KEYWORD, TT_identifier, _Bool, VARIABLEOP,TT_STRING
from Error import SyntaxError
import collections
from ParserNodes import *

class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None

    def register(self, res):
        if isinstance(res, ParseResult):
            if res.error:
                self.error = res.error
            return res.node
        return res

    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        self.error = error
        return self


class Parser:
    def __init__(self, tokenStream):
        self.tokens = tokenStream
        self.position = -1
        self.currentToken = None
        self.Advance()

    def Advance(self):
        self.position += 1
        if self.position < len(self.tokens):
            self.currentToken = self.tokens[self.position]
        return self.currentToken

    def Parse(self):
        res = self.newOp(0)
        if not res.error and self.currentToken.dataType != EOF:
            return res.failure(SyntaxError(f"There is a typo in the program"))
        return res

    def isNotLogicalCondition(self, if_condition):
        if not isinstance(if_condition, (BinOpNode, BoolNode)):
            return True
        if isinstance(if_condition, (BinOpNode)) and if_condition.op_tok.dataType not in (TT_OP["=="], TT_OP[">"], TT_OP["<"], TT_OP["<="], TT_OP[">="]):
            return True
        return False

    def ifstate(self):
        res = ParseResult()
        cases = collections.deque()
        elseCase = None
        while self.currentToken.dataType == KEYWORD["IF"] or self.currentToken.dataType == KEYWORD["ELIF"]:
            res.register(self.Advance())
            if_condition = res.register(self.newOp(0))
            if self.isNotLogicalCondition(if_condition):
                return res.failure(SyntaxError(f"condition must be a logical condition!"))
            if res.error:
                return res
            if self.currentToken.dataType is not KEYWORD["THEN"]:
                return res.failure(SyntaxError(f"Must have keyword \"Then\" after {if_condition}"))
            res.register(self.Advance())
            expr = res.register(self.newOp(0))
            if res.error:
                return res
            cases.append((if_condition, expr))
        if self.currentToken.dataType == KEYWORD["ELSE"]:
            res.register(self.Advance())
            expr = res.register(self.newOp(0))
            if res.error:
                return res
            elseCase = expr
        return res.success(IfLoopNode(cases, elseCase))

    def whilestate(self):
        res = ParseResult()
        res.register(self.Advance())
        if_condition = res.register(self.newOp(0))
        if res.error:
            return res
        if self.isNotLogicalCondition(if_condition):
            return res.failure(SyntaxError(f"condition must be a logical condition!"))
        if self.currentToken.dataType is not KEYWORD["THEN"]:
            return res.failure(SyntaxError(f"Must have keyword \"Then\" after {if_condition}"))
        res.register(self.Advance())
        expression = res.register(self.newOp(0))
        if res.error:
            return res
        return res.success(WhileNode(if_condition, expression))

    def currentTokenIsNotComma(self):
        return self.currentToken.dataType is not TT_OP[","]

    def forstate(self):
        res = ParseResult()
        res.register(self.Advance())
        variableAssignment = res.register(self.newOp(0))
        if res.error:
            return res
        if not isinstance(variableAssignment, VarAssignNode):
            return res.failure(SyntaxError("first argument of for loop must be a variable assignment"))
        if self.currentTokenIsNotComma():
            return res.failure(SyntaxError("no comma separation"))
        res.register(self.Advance())
        condition = res.register(self.newOp(0))
        if res.error:
            return res
        if self.isNotLogicalCondition(condition):
            return res.failure(SyntaxError("second argument of for loop must be a condition"))
        if self.currentTokenIsNotComma():
            return res.failure(SyntaxError("no comma separation"))
        res.register(self.Advance())
        compoundOperation = res.register(self.newOp(0))
        if res.error:
            return res
        if not isinstance(compoundOperation, variableOpNode):
            return res.failure(SyntaxError("third argument of for loop must be a compound operation of a variable"))
        if self.currentToken.dataType is not KEYWORD["THEN"]:
            return res.failure(SyntaxError("Add a THEN key word in between the FOR expression and the following expression"))
        res.register(self.Advance())
        expression = res.register(self.newOp(0))
        if res.error:
            return res
        return res.success(ForLoop(variableAssignment, condition, compoundOperation, expression))

    def getArguments(self):
        res = ParseResult()
        res.register(self.Advance())
        arguments = []
        argument = res.register(self.newOp(0))
        if res.error: return res
        while True:
            arguments.append(argument)
            if self.currentToken.dataType is TT_OP[")"]:
                break
            res.register(self.Advance())
            argument = res.register(self.newOp(0))
            if res.error: return res
        if self.currentToken.dataType != TT_OP[")"]:
            return res.failure(SyntaxError("Expected \")\" after arguments"))
        return res.success(arguments)
        
    def factor(self):
        res = ParseResult()
        tok = self.currentToken
        # check is unary operation
        if self.currentToken.dataType in (TT_OP["+"], TT_OP["-"]):
            res.register(self.Advance())
            factor = res.register(self.factor())
            if res.error:
                return res
            return res.success(UnaryOpNode(tok, factor))
        #check is number
        elif self.currentToken.dataType == TT_NUM:
            res.register(self.Advance())
            return res.success(NumberNode(tok))
        #check is variable
        elif self.currentToken.dataType == TT_identifier:
            if self.peek().dataType == TT_OP["("]:
                name = self.currentToken
                res.register(self.Advance())
                arguments = res.register(self.getArguments())
                if res.error: return res
                else: 
                    res.register(self.Advance())
                    return res.success(callFunctionNode(name,arguments))
            res.register(self.Advance())
            return res.success(VarAcessNode(tok))
        #check is string
        elif tok.dataType == TT_STRING:
            res.register(self.Advance())
            return res.success(StringNode(tok))
        # check bool
        elif self.currentToken.dataType == KEYWORD["TRUE"] or self.currentToken.dataType == KEYWORD["FALSE"]:
            res.register(self.Advance())
            return res.success(BoolNode(tok))
        #check NULL
        elif self.currentToken.dataType == KEYWORD["NULL"]:
            res.register(self.Advance())
            return res.success(NullNode())
        # check is a bracket
        elif self.currentToken.dataType == TT_OP["("]:
            res.register(self.Advance())
            expression = res.register(self.newOp(0))
            if res.error:
                return res
            if self.currentToken.dataType == TT_OP[")"]:
                res.register(self.Advance())
                return res.success(expression)
            else:
                return res.failure(SyntaxError("no closing brackets found"))
        return res.failure(SyntaxError(f"Expected a value but got something else instead"))

    def newOp(self, precedence):
        keyWords = tuple([str(i.name)
                          for i in KEYWORD.values() if i.precedence == precedence])
        operators = tuple([str(i.name)
                           for i in TT_OP.values() if i.precedence == precedence])
        variableOperators = tuple(
            [str(i.name) for i in VARIABLEOP.values() if i.precedence == precedence])
        if variableOperators and self.currentToken.dataType == TT_identifier:
            result = self.VariableOp(variableOperators, precedence)
            if result != None:
                return result
        for i in keyWords:
            if self.currentToken.dataType.name == i:
                method = getattr(self, i.lower())
                return method()
        if precedence == max_precedence:
            return self.BinaryOp(self.factor, (operators))
        return self.BinaryOp(lambda: self.newOp(precedence + 1), operators)

    def function(self):
        res = ParseResult()
        name = self.peek()
        if name.dataType is TT_identifier:
            res.register(self.Advance())
        if name.dataType is not TT_identifier:
            name = None
        res.register(self.Advance())
        if not self.currentToken.dataType == TT_OP["("]:
            return res.failure(SyntaxError("Expected \"(\" after function name"))
        res.register(self.Advance())
        Arguments = []
        while self.currentToken.dataType == TT_identifier:
            Arguments.append(self.currentToken)
            res.register(self.Advance())
            res.register(self.Advance())
        if not self.currentToken.dataType ==KEYWORD["THEN"]:
            return res.failure(SyntaxError("expected \"THEN\" after function call"))
        res.register(self.Advance())
        expresion = res.register(self.newOp(0))
        if res.error: return res
        return FunctionNode(name,Arguments,expresion)

    def createvar(self):
        res = ParseResult()
        res.register(self.Advance())
        if self.currentToken.dataType.name != TT_identifier.name:
            return res.failure("Expected identifier to variable")
        var_name = self.currentToken
        res.register(self.Advance())
        if self.currentToken.dataType.name != TT_OP["="].name:
            return res.failure(f"Expected equal operator sign after identifier,{self.currentToken}")
        res.register(self.Advance())
        expression = res.register(self.newOp(0))
        if res.error:
            return res
        return res.success(VarAssignNode(var_name, expression))

    def peek(self):
        return self.tokens[self.position + 1]

    def VariableOp(self, ops, precedence):
        res = ParseResult()
        if self.peek().dataType.name in ops:
            left = res.register(self.newOp(precedence+1))
            op = self.currentToken
            res.register(self.Advance())
            right = res.register(self.newOp(precedence+1))
            return res.success(variableOpNode(left, op, right))
        else:
            return None

    def BinaryOp(self, func, ops):
        res = ParseResult()
        left = res.register(func())
        if res.error:
            return res
        while self.currentToken.dataType.name in ops:
            operator = self.currentToken
            res.register(self.Advance())
            right = res.register(func())
            if res.error:
                return res
            left = BinOpNode(left, operator, right)
        return res.success(left)
