from typing import List, Tuple, Dict

from .ast_if_elif import ASTIfElif
from .ast_isub_int import ASTIsubInt
from .ast_set_var import ASTSetVar
from .code_buffer import CodeBuffer
from .code_getters import IGetter
from .code_stack import Stack
from .code_var import CodeVar
from .iprocessable import IProcessable


class ASTCase(IProcessable):
    def __init__(self, test_var: IGetter, code: List[Tuple[int, List[IProcessable]]]):
        self.test_var: IGetter = test_var
        self.code: List[Tuple[int, List[IProcessable]]] = code

    def process(self, declarations: Dict[str, CodeVar], stack: Stack, out: CodeBuffer) -> None:
        if len(self.code) != 0:
            copy_var = stack.push()
            out.write(ASTSetVar([copy_var], self.test_var))
            last = 0
            for i in self.code:
                out.write(ASTIsubInt([copy_var], i[0] - last))
                out.write(ASTIfElif([(copy_var, [])], code_else=i[1]))
                last = i[0]

            stack.pop(copy_var)
