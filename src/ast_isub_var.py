from typing import List, Dict

from .ast_iadd_int import ASTIaddInt
from .ast_isub_int import ASTIsubInt
from .ast_set_int import ASTSetInt
from .base_ast import ASTWhile
from .code_buffer import CodeBuffer
from .code_getters import IGetter
from .code_stack import Stack
from .code_var import CodeVar
from .iprocessable import IProcessable


class ASTIsubVar(IProcessable):
    def __init__(self, names: List[IGetter], right: IGetter):
        self.names: List[IGetter] = names
        self.right: IGetter = right

    def __str__(self):
        return f"{str(self.names)[1:-1]} -= {self.right}"

    def process(self, declarations: Dict[str, CodeVar], stack: Stack, out: CodeBuffer) -> None:
        copy_var = stack.push()
        out.write(ASTSetInt([copy_var], 0))

        out.write(
            ASTWhile(self.right, [
                ASTIsubInt([self.right], 1),
                ASTIsubInt(self.names, 1),
                ASTIaddInt([copy_var], 1)
            ]))

        out.write(
            ASTWhile(copy_var, [
                ASTIsubInt([copy_var], 1),
                ASTIaddInt([self.right], 1)
            ]))

        stack.pop(copy_var)
