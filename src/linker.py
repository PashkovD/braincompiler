from .code_ast import ASTFile
from .goto import Goto
from .util import bf_move


class CodeLinker:
    def __init__(self, code: ASTFile):
        self.code: ASTFile = code

    def process(self) -> str:
        code, declarations = self.code.process()
        pos = 0
        data = ""
        for i in code:
            if isinstance(i, str):
                data += i
                continue
            if isinstance(i, Goto):
                var = i.var.get_var(declarations).pos
                data += bf_move(var - pos)
                pos = var
                continue

            raise Exception

        return data
