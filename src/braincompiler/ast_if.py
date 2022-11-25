from typing import List, Dict

from .ast_set_int import ASTSetInt
from .ast_set_var import ASTSetVar
from .base_ast import ASTWhile
from .code_buffer import CodeBuffer
from .code_getters import IGetter
from .code_stack import Stack
from .code_var import CodeVar
from .iprocessable import IProcessable


class ASTIf(IProcessable):
    def __init__(self, test_var: IGetter, code: List[IProcessable]):
        self.test_var: IGetter = test_var
        self.code: List[IProcessable] = code

    def __str__(self):
        return f"if({self.test_var})"

    def process(self, declarations: Dict[str, CodeVar], stack: Stack, out: CodeBuffer) -> None:
        copy_var = stack.push()
        out.write(ASTSetVar([copy_var], self.test_var))
        out.write(ASTWhile(copy_var, self.code + [ASTSetInt([copy_var], 0)]))
        stack.pop(copy_var)
