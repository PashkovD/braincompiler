from typing import List, Dict

from .ast_if_elif import ASTIfElif
from .ast_isub_int import ASTIsubInt
from .ast_isub_var import ASTIsubVar
from .ast_set_int import ASTSetInt
from .ast_set_var import ASTSetVar
from .base_ast import ASTWhile
from .code_buffer import CodeBuffer
from .code_getters import IGetter
from .code_stack import Stack
from .code_var import CodeVar
from .iprocessable import IProcessable


class ASTImodInt(IProcessable):
    def __init__(self, names: List[IGetter], num: int):
        self.names: List[IGetter] = names
        self.num: int = num

    def process(self, declarations: Dict[str, CodeVar], stack: Stack, out: CodeBuffer) -> None:
        for left in self.names:
            if self.num == 0:
                out.write(ASTSetInt([left], -1))
                continue

            work = stack.push()
            out.write(ASTSetInt([work], 1))
            left_var = stack.push()
            out.write(ASTSetVar([left_var], left))
            right_var = stack.push()

            out.write(ASTWhile(work, [
                ASTSetInt([right_var], self.num),
                ASTWhile(right_var, [
                    ASTIfElif([(left_var, [])], code_else=[
                        ASTSetInt([work], 0),
                        ASTSetInt([left], self.num),
                        ASTIsubVar([left], right_var),
                        ASTSetInt([left_var, right_var], 1),
                    ]),
                    ASTIsubInt([left_var, right_var], 1),
                ]),
            ]))
            stack.pop(right_var)
            stack.pop(left_var)
            stack.pop(work)
