from typing import List, Dict

from .ast_iadd_int import ASTIaddInt
from .ast_if import ASTIf
from .ast_if_elif import ASTIfElif
from .ast_isub_int import ASTIsubInt
from .ast_set_int import ASTSetInt
from .ast_set_var import ASTSetVar
from .base_ast import ASTWhile
from .code_buffer import CodeBuffer
from .code_getters import IGetter
from .code_stack import Stack
from .code_var import CodeVar
from .iprocessable import IProcessable


class ASTIdivVar(IProcessable):
    def __init__(self, names: List[IGetter], right: IGetter):
        self.names: List[IGetter] = names
        self.right: IGetter = right

    def process(self, declarations: Dict[str, CodeVar], stack: Stack, out: CodeBuffer) -> None:
        for left in self.names:
            work = stack.push()
            out.write(ASTSetInt([work], 1))
            counter = stack.push()
            out.write(ASTSetInt([counter], 0))
            left_var = stack.push()
            out.write(ASTSetVar([left_var], left))
            right_var = stack.push()

            out.write(ASTIf(self.right, [
                ASTWhile(work, [
                    ASTSetVar([right_var], self.right),
                    ASTWhile(right_var, [
                        ASTIfElif([(left_var, [])], code_else=[
                            ASTSetInt([work], 0),
                            ASTSetInt([left_var, right_var], 1),
                        ]),
                        ASTIsubInt([left_var, right_var], 1),
                    ]),
                    ASTIaddInt([counter], 1),
                ])
            ]))
            out.write(ASTIsubInt([counter], 1))
            out.write(ASTSetVar([left], counter))
            stack.pop(right_var)
            stack.pop(left_var)
            stack.pop(counter)
            stack.pop(work)
