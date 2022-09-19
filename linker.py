from typing import Dict

from code_ast import ASTFile
from goto import Goto
from util import bf_move


class CodeLinker:
    def __init__(self, code: ASTFile):
        self.code: ASTFile = code

    def process(self) -> str:
        pos = 0
        decls: Dict[str, int] = {f.name: i for i, f in enumerate(self.code.declarations)}
        data = ""
        for i in self.code.process():
            if isinstance(i, str):
                data += i
                continue
            if not isinstance(i, Goto):
                raise Exception

            data += bf_move(decls[i.name]-pos)
            pos = decls[i.name]

        return data
