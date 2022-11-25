from typing import Dict, List

from .ast_case import ASTCase
from .ast_set_var import ASTSetVar
from .code_buffer import CodeBuffer
from .code_getters import IGetter, IndexGetter
from .code_stack import Stack
from .code_types import StringCodeType
from .code_var import CodeVar
from .iprocessable import IProcessable


class ASTListGetVar(IProcessable):
    def __init__(self, names: List[IGetter], right: IGetter, index: IGetter):
        self.names: List[IGetter] = names
        self.right: IGetter = right
        self.index: IGetter = index

    def process(self, declarations: Dict[str, CodeVar], stack: Stack, out: CodeBuffer) -> None:
        var: CodeVar = self.right.get_var(declarations)
        assert isinstance(var.type, StringCodeType)
        out.write(
            ASTCase(self.index, [
                (i, [ASTSetVar(self.names, IndexGetter(self.right, i))])
                for i in range(var.type.len_)
            ]))
