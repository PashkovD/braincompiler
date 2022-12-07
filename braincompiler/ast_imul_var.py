from typing import List, Dict

from .ast_iadd_var import ASTIaddVar
from .ast_isub_int import ASTIsubInt
from .ast_set_int import ASTSetInt
from .ast_set_var import ASTSetVar
from .base_ast import ASTWhile
from .code_buffer import CodeBuffer
from .code_getters import IGetter
from .code_stack import Stack
from .code_var import CodeVar
from .iprocessable import IProcessable


class ASTImulVar(IProcessable):
    def __init__(self, names: List[IGetter], right: IGetter):
        self.names: List[IGetter] = names
        self.right: IGetter = right

    def process(self, declarations: Dict[str, CodeVar], stack: Stack, out: CodeBuffer) -> None:
        for left in self.names:
            copy_var = stack.push()
            copy_var2 = stack.push()
            out.write(ASTSetVar([copy_var], left))
            out.write(ASTSetVar([copy_var2], self.right))
            out.write(ASTSetInt([left], 0))
            out.write(ASTWhile(copy_var2, [
                ASTIsubInt([copy_var2], 1),
                ASTIaddVar([left], copy_var),
            ]))
            stack.pop(copy_var2)
            stack.pop(copy_var)
