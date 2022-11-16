from typing import List, Dict

from .ast_ilshift_int import ASTIlshiftInt
from .ast_isub_int import ASTIsubInt
from .ast_set_var import ASTSetVar
from .base_ast import ASTWhile
from .code_buffer import CodeBuffer
from .code_getters import IGetter
from .code_stack import Stack
from .code_var import CodeVar
from .iprocessable import IProcessable


class ASTIlshiftVar(IProcessable):
    def __init__(self, names: List[IGetter], right: IGetter):
        self.names: List[IGetter] = names
        self.right: IGetter = right

    def process(self, declarations: Dict[str, CodeVar], stack: Stack, out: CodeBuffer) -> None:
        copy_var = stack.push()
        out.write(ASTSetVar([copy_var], self.right))
        out.write(ASTWhile(copy_var, [
            ASTIsubInt([copy_var], 1),
            ASTIlshiftInt(self.names, 1),
        ]))
        stack.pop(copy_var)
