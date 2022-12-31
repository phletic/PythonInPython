class Error:
    def __init__(self,text,errType):
        self.text = text
        self.type = errType
    
    def __repr__(self):
        return f'{self.type} : {self.text}'

class IllegalChar(Error):
    def __init__(self,text):
        super().__init__(text,"Illegal Character")

class NumberError(Error):
    def __init__(self,text):
        super().__init__(text,"Number Error")

class SyntaxError(Error):
    def __init__(self,text):
        super().__init__(text,"Syntax Error") 

class RTError(Error):
    def __init__(self,text):
        super().__init__(text,"Runtime Error")

class KeyboardInterruptErr(Error):
    def __init__(self):
        super().__init__("Keyboard Interupt","Keyboard Interupt")

class StackOverflow(Error):
    def __init__(self,text):
        super().__init__(text,"Stack Overflow")