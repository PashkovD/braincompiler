from typing import List, Dict

from .ast_set_int import ASTSetInt
from .code_buffer import CodeBuffer
from .code_getters import IGetter
from .code_stack import Stack
from .code_var import CodeVar
from .goto import Goto
from .iprocessable import IProcessable


class ASTSetVar(IProcessable):
    def __init__(self, names: List[IGetter], right: IGetter):
        self.names: List[IGetter] = names
        self.right: IGetter = right

    def __str__(self):
        return f"{str(self.names)[1:-1]} = {self.right}"

    def process(self, declarations: Dict[str, CodeVar], stack: Stack, out: CodeBuffer) -> None:
        out.write(ASTSetInt(self.names, 0))

        copy_var = stack.push()
        out.write(ASTSetInt([copy_var], 0))
        out.write(Goto(self.right))
        out.write("[-")
        for i in self.names:
            out.write(Goto(i))
            out.write("+")
        out.write(Goto(copy_var))
        out.write("+")
        out.write(Goto(self.right))
        out.write("]")

        out.write(Goto(copy_var))
        out.write("[-")
        out.write(Goto(self.right))
        out.write("+")
        out.write(Goto(copy_var))
        out.write("]")

        stack.pop(copy_var)
