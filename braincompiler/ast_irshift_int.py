from typing import List, Dict

from .ast_idiv_int import ASTIdivInt
from .code_buffer import CodeBuffer
from .code_getters import IGetter
from .code_stack import Stack
from .code_var import CodeVar
from .iprocessable import IProcessable


class ASTIrshiftInt(IProcessable):
    def __init__(self, names: List[IGetter], num: int):
        self.names: List[IGetter] = names
        self.num: int = num

    def process(self, declarations: Dict[str, CodeVar], stack: Stack, out: CodeBuffer) -> None:
        if self.num == 0:
            return
        out.write(ASTIdivInt(self.names, 2 ** self.num))
