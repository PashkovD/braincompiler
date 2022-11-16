from typing import List, Dict

from .ast_iadd_int import ASTIaddInt
from .code_buffer import CodeBuffer
from .code_getters import IGetter
from .code_stack import Stack
from .code_var import CodeVar
from .goto import Goto
from .iprocessable import IProcessable


class ASTSetInt(IProcessable):
    def __init__(self, names: List[IGetter], num: int):
        self.names: List[IGetter] = names
        self.num: int = num

    def __str__(self):
        return f"{str(self.names)[1:-1]} = {self.num}"

    def process(self, declarations: Dict[str, CodeVar], stack: Stack, out: CodeBuffer) -> None:
        for i in self.names:
            out.write(Goto(i))
            out.write("[-]")
            out.write(ASTIaddInt([i], self.num))
