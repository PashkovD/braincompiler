from typing import List, Tuple, Dict

from .ast_if import ASTIf
from .ast_set_int import ASTSetInt
from .code_buffer import CodeBuffer
from .code_getters import IGetter
from .code_stack import Stack
from .code_var import CodeVar
from .iprocessable import IProcessable


class ASTIfElif(IProcessable):
    def __init__(self, data: List[Tuple[IGetter, List[IProcessable]]], code_else: List[IProcessable] = None):
        self.data: List[Tuple[IGetter, List[IProcessable]]] = data
        self.code_else: List[IProcessable] = code_else

    def __str__(self):
        return f"if({self.data[0][0]})" + \
               "".join(f"elif({i[0]})" for i in self.data) + \
               f"else" if self.code_else is not None else ""

    def process(self, declarations: Dict[str, CodeVar], stack: Stack, out: CodeBuffer) -> None:
        else_flag = stack.push()
        out.write(ASTSetInt([else_flag], 1))
        out.write(ASTIf(self.data[0][0], self.data[0][1] + [ASTSetInt([else_flag], 0)]))
        for i in self.data[1:]:
            out.write(ASTIf(
                else_flag,
                [ASTIf(i[0], i[1] + [ASTSetInt([else_flag], 0)])]
            ))
        if self.code_else is not None:
            out.write(ASTIf(else_flag, self.code_else))
        stack.pop(else_flag)
