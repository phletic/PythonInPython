from lexerAnalysis import Lexer
from Parser import Parser
from interpreter import Interpreter
from symbolTable import SymbolTable
from Error import KeyboardInterruptErr
ST = SymbolTable()


def run(text):
    text = text.strip()
    try:
        # Generate tokens
        lexer = Lexer(text)
        error, tokens = lexer.tokenize()
        if error:
            return error[0]
        print(tokens)
        parser = Parser(tokens)
        ast = parser.Parse()
        if ast.error:
            return ast.error
        print(ast.node)
        interpreter = Interpreter(ST)
        number = interpreter.visit(ast.node)
        if number.error:
            return number.error
        res = number.value
        print(interpreter.symbolTable.symbols)
        if res == None:
            return ''
        return res
    except KeyboardInterrupt:
        return KeyboardInterruptErr()