from typing import List, Dict

from .ast_iadd_var import ASTIaddVar
from .ast_imul_var import ASTImulVar
from .ast_set_int import ASTSetInt
from .ast_set_var import ASTSetVar
from .code_buffer import CodeBuffer
from .code_getters import IGetter
from .code_stack import Stack
from .code_var import CodeVar
from .iprocessable import IProcessable


class ASTImulInt(IProcessable):
    def __init__(self, names: List[IGetter], num: int):
        self.names: List[IGetter] = names
        self.num: int = num

    def process(self, declarations: Dict[str, CodeVar], stack: Stack, out: CodeBuffer) -> None:
        if self.num == 0:
            out.write(ASTSetInt(self.names, 0))
            return

        if abs(self.num) >= 16:
            copy_var = stack.push()
            out.write(ASTSetInt([copy_var], self.num))
            out.write(ASTImulVar(self.names, copy_var))
            stack.pop(copy_var)
            return

        for left in self.names:
            copy_var = stack.push()
            out.write(ASTSetVar([copy_var], left))
            for _ in range(self.num - 1):
                out.write(ASTIaddVar([left], copy_var))
            stack.pop(copy_var)
