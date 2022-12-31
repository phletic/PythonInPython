from Error import RTError
import sys


class symbol:
    def __init__(self, name, op=None, precedence=None, function=None,isDataType = False):
        self.name = name
        self.precedence = precedence
        self.function = function
        self.op = op
        self.dataType = isDataType

    def __repr__(self):
        return self.name


max_precedence = 12
TT_OP = {
    "(": symbol("LBRACOP", "("),
    ")": symbol("RBRACOP", ")"),
    ",":symbol("COMMA",","),
    "\"":symbol("STRING","\""),
    "**": symbol("POWEROP", "**", 12, "power"),
    "*": symbol("MULOP", "*", 11, "mul"),
    "/": symbol("DIVOP", "/", 11, "div"),
    "+": symbol("PLUSOP", "+", 10, "add"),
    "-": symbol("NEGATEOP", "-", 10, "sub"),
    "<": symbol("LESSTHAN", "<", 10, "less_than"),
    ">": symbol("MORETHAN", ">", 10, "more_than"),
    ">=": symbol("MORE/EQUALTHAN", ">=", 10, "more_than_or_equal_to"),
    "<=": symbol("LESS/EQUALTHAN", "<=", 9, "less_than_or_equal_to"),
    "==": symbol("EQUALTO", "==", 8, "is_equal"),
    "<<": symbol("LSHIFT", "<<", 7, "left_shift"),
    ">>": symbol("RSHIFT", ">>", 7, "right_shift"),
    "&": symbol("BAND", "&", 6, "_and"),
    "^": symbol("BXOR", "^", 5, "_xor"),
    "|": symbol("BOR", "|", 4, "_or"),
    "&&": symbol("LAND", "&&", 3, "L_and"),
    "||": symbol("LOR", "||", 2, "L_or"),
    "=": symbol("ASIGNMENTOP", "=", 1),
}

VARIABLEOP = {
    "+=": symbol("CSUM", "+=", 1, "add"),
    "-=": symbol("CSUB", "-=", 1, "sub"),
    "*=": symbol("CMUL", "*=", 1, "mul"),
    "/=": symbol("CDIV", "/=", 1, "div"),
}

KEYWORD = {
    "LET": symbol("CREATEVAR", precedence=11),
    "IF": symbol("IFSTATE", precedence=11),
    "FUNCTION" : symbol("FUNCTION",precedence=11),
    "THEN": symbol("THEN"),
    "ELIF": symbol("ELIF"),
    "ELSE": symbol("ELSE"),
    "FOR": symbol("FORSTATE", precedence=0),
    "WHILE": symbol("WHILESTATE", precedence=0),
    "TRUE": symbol("TRUEBOOL",isDataType=True),
    "FALSE": symbol("FALSEBOOL",isDataType=True),
    "NULL": symbol("NULL",isDataType=True)
}
TT_identifier = symbol("ID")
TT_STRING = symbol("str")
#TT_KEYWORD = symbol("KEY",precedence=5)
TT_NUM = symbol("NUM",isDataType=True)
EOF = symbol("EOF")


class DataType():
    def __init__(self, val):
        self.val = val

    def add(self, other):
        return self.noImp(other)

    def sub(self, other):
        return self.noImp(other)

    def mul(self, other):
        return self.noImp(other)

    def div(self, other):
        return self.noImp(other)

    def negate(self, other):
        return self.noImp(other)

    def power(self, val):
        return self.noImp(val)

    def left_shift(self, other):
        return self.noImp(other)

    def right_shift(self, other):
        return self.noImp(other)

    def _and(self, other):
        return self.noImp(other)

    def _or(self, other):
        return self.noImp(other)

    def _xor(self, other):
        return self.noImp(other)

    def is_equal(self, other):
        return self.noImp(other)

    def less_than_or_equal_to(self, other):
        return self.noImp(other)

    def more_than_or_equal_to(self, other):
        return self.noImp(other)

    def more_than(self, other):
        return self.noImp(other)

    def less_than(self, other):
        return self.noImp(other)

    def L_and(self, other):
        return self.noImp(other)

    def L_or(self, other):
        return self.noImp(other)

    def noImp(self, other):
        return None, RTError(f"Data Type, {type(self).__name__}, has no such operator")

class NULL(DataType):
    def __init__(self,shouldRepresent):
        super().__init__("NULL")
        self.shouldRepresent = shouldRepresent
    
    def __repr__(self):
        if self.shouldRepresent:
            return "NULL"
        else:
            return ''
class String(DataType):
    def __init__(self,val):
        super().__init__(val)
    
    def __repr__(self):
        return str(self.val)

class Number(DataType):
    def __init__(self, val):
        super().__init__(val)
        
    def add(self, other):
        if isinstance(other, (Number, _Bool)):
            return Number(self.val + other.val), None
        else:
            return None, RTError(f"Given wrong data type. expected float but got {type(other).__name__}")

    def sub(self, other):
        if isinstance(other, (Number, _Bool)):
            return Number(self.val - other.val), None
        else:
            return None, RTError(f"Given wrong data type. expected float but got {type(other).__name__}")

    def mul(self, other):
        if isinstance(other, (Number, _Bool)):
            return Number(self.val * other.val), None
        else:
            return None, RTError(f"Given wrong data type. expected float but got {type(other).__name__}")

    def div(self, other):
        if isinstance(other, (Number, _Bool)):
            if other.val == 0:
                return None, RTError("Division by zero error")
            return Number(self.val / other.val), None
        else:
            return None, RTError(f"Given wrong data type. expected float but got {type(other).__name__}")

    def negate(self, op):
        return Number(self.val * -1) if op == TT_OP["-"] else self, None

    def power(self, other):
        if isinstance(other,(Number,_Bool)):
            return Number(self.val**other.val), None
        else:
            return None, RTError(f"Given wrong data type. expected float but got {type(other).__name__}")

    def left_shift(self, other):
        if other.val < 0:
            return None, RTError("negative shift not accepted")
        return Number(int(self.val) << int(other.val)), None

    def right_shift(self, other):
        if other.val < 0:
            return None, RTError("negative shift not accepted")
        return Number(int(self.val) >> int(other.val)), None

    def _and(self, other):
        return Number(int(self.val) & int(other.val)), None

    def _or(self, other):
        return Number(int(self.val) | int(other.val)), None

    def _xor(self, other):
        return Number(int(self.val) ^ int(other.val)), None

    def is_equal(self, other):
        if isinstance(other, (Number, _Bool)):
            condition = _Bool(
                "TRUE") if self.val == other.val else _Bool("FALSE")
            return condition, None
        else:
            return None, RTError(f"Given wrong data type. expected float but got {type(other).__name__}")

    def less_than_or_equal_to(self, other):
        if isinstance(other, (Number, _Bool)):
            return _Bool("TRUE") if self.val <= other.val else _Bool("FALSE"), None
        else:
            return None, RTError(f"Given wrong data type. expected float but got {type(other).__name__}")

    def more_than_or_equal_to(self, other):
        if isinstance(other, (Number, _Bool)):
            return _Bool("TRUE") if self.val >= other.val else _Bool("FALSE"), None
        else:
            return None, RTError(f"Given wrong data type. expected float but got {type(other).__name__}")

    def more_than(self, other):
        if isinstance(other, (Number, _Bool)):
            return _Bool("TRUE") if self.val > other.val else _Bool("FALSE"), None
        else:
            return None, RTError(f"Given wrong data type. expected float but got {type(other).__name__}")

    def less_than(self, other):
        if isinstance(other, (Number, _Bool)):
            return _Bool("TRUE") if self.val < other.val else _Bool("FALSE"), None
        else:
            return None, RTError(f"Given wrong data type. expected float but got {type(other).__name__}")

    def L_or(self, other):
        if isinstance(other, (Number, _Bool)):
            res = self.val or other.val
            if res > 1:
                return None, Number(res)
            return _Bool("TRUE") if res == 1 else _Bool("FALSE"), None
        else:
            return None, RTError(f"Given wrong data type. expected float but got {type(other).__name__}")

    def L_and(self, other):
        if isinstance(other, (Number, _Bool)):
            res = self.val and other.val
            if res > 1:
                return Number(res), None
            return _Bool("TRUE") if res == 1 else _Bool("FALSE"), None
        else:
            return None, RTError(f"Given wrong data type. expected float but got {type(other).__name__}")

    def __repr__(self):
        return str(self.val)


class _Bool(Number):
    def __init__(self, val):
        super().__init__(val)
        if self.val == "TRUE":
            self.val = 1
        elif self.val == "FALSE":
            self.val = 0

    def __repr__(self):
        return "TRUE" if self.val == 1 else "FALSE"

class Function(DataType):
    def __init__(self,name,arguments,expression):
        self.name = name
        self.arguments = arguments
        self.expression = expression
    def __repr__(self):
        return f"<function : {self.name}>"