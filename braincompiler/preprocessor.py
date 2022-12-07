from typing import List, Dict

from .lexer import CodeLexer


class Preprocessor:
    def __init__(self, code: List = None, declarations: Dict[str, List] = None):
        self.code = code if code is not None else []
        self.declarations = declarations if declarations is not None else {}

        self.token_pos = 0

    def process(self):
        pos = 0
        while pos < len(self.code):
            if self.code[pos].type == 'DEFINE':
                line: int = self.code[pos].lineno
                self.code.pop(pos)
                if not pos < len(self.code) or not self.code[pos].type == "ID":
                    raise Exception(f"{line}: missing ID after #define")
                name: str = self.code[pos].value
                if name in self.declarations.keys():
                    raise Exception(f"{line}: {name} is exist")
                self.code.pop(pos)
                self.declarations[name] = []
                while pos < len(self.code) and self.code[pos].lineno == line:
                    self.declarations[name].append(self.code[pos])
                    self.code.pop(pos)
            elif self.code[pos].type == 'ID' and self.code[pos].value in self.declarations.keys():
                name: str = self.code[pos].value
                self.code.pop(pos)
                self.code = self.code[:pos] + self.declarations[name] + self.code[pos:]
            else:
                pos += 1

    def input(self, data: str):
        lexer = CodeLexer()
        lexer.lexer.input(data)
        self.code = list(lexer.lexer)
        self.process()

    def token(self):
        if not self.token_pos < len(self.code):
            return None
        self.token_pos += 1
        return self.code[self.token_pos - 1]
