import string
from dataTypes import TT_OP, TT_NUM, EOF, TT_identifier, KEYWORD, VARIABLEOP, TT_STRING
from Error import IllegalChar, NumberError
letters_digits = string.digits + string.ascii_letters


class Token():
    def __init__(self, dataType, val):
        self.dataType = dataType
        self.val = val

    def __repr__(self):
        return f'{self.dataType}:{self.val}'

    def match(self, value):
        return self.dataType == value.dataType and self.val == value.val


class Lexer:
    def __init__(self, text):
        self.text = text
        self.currentChar = None
        self.errors = []
        self.position = -1

    def Advance(self,skipSpace = True):
        self.position += 1
        self.currentChar = self.text[self.position]
        if self.currentChar in " " and skipSpace:
            self.Advance()
        if self.currentChar in "\t\n":
            self.Advance()

    def peekNext(self):
        return self.text[self.position + 1]

    def tokenize(self):
        tokens = []
        while self.position + 1 < len(self.text) and not self.errors:
            self.Advance()
            tokens.append(self.TokenizeChar())
        tokens.append(Token(EOF, None))
        return self.errors, tokens

    def numberToken(self):
        current_digit = ''
        dotCount = 0
        while self.currentChar in string.digits + ".":
            if self.currentChar == '.':
                dotCount += 1
            current_digit += self.currentChar
            if self.position + 1 == len(self.text):
                break
            if self.peekNext() not in string.digits + ".":
                break
            else:
                self.Advance()
        if dotCount > 1:
            self.errors.append(NumberError(
                f'{current_digit} is an invalid number'))
            return "ERR"
        return Token(TT_NUM, float(current_digit))

    def TokenizeChar(self):
        twoDigit = self.currentChar + \
            self.text[self.position+1] if self.position + \
            1 < len(self.text) else None
        if self.currentChar.isdigit():
            return self.numberToken()
        elif self.currentChar in letters_digits:
            return self.make_indentifier()
        elif self.currentChar == TT_OP["\""].op:
            return self.makeString()
        elif twoDigit in VARIABLEOP:
            self.Advance()
            return Token(VARIABLEOP[twoDigit], twoDigit)
        elif twoDigit in TT_OP:
            self.Advance()
            return Token(TT_OP[twoDigit], twoDigit)
        elif self.currentChar in TT_OP:
            return Token(TT_OP[self.currentChar], self.currentChar)
        else:
            self.errors.append(IllegalChar(
                f'{self.currentChar} cannot be understood'))
            return "ERR"

    def makeString(self):
        string = ""
        self.Advance()
        while self.currentChar != "\"":
            string += self.currentChar
            self.Advance(skipSpace=False)
        return Token(TT_STRING, string)

    def make_indentifier(self):
        id_string = ''
        while self.currentChar in letters_digits+"_":
            id_string += self.currentChar
            if self.position + 1 == len(self.text):
                break
            # if self.text[self.position + 1] in " \t\n":
            #    break
            if self.peekNext() not in letters_digits+"_":
                break
            else:
                self.Advance()
        return Token(KEYWORD[id_string], id_string) if id_string in KEYWORD else Token(TT_identifier, id_string)


if __name__ == "__main__":
    analyser = Lexer("(1+1)*3")
    print(analyser.tokenize())
