from typing import Dict

from .ast_case import ASTCase
from .ast_set_var import ASTSetVar
from .code_buffer import CodeBuffer
from .code_getters import IGetter, IndexGetter
from .code_stack import Stack
from .code_types import StringCodeType
from .code_var import CodeVar
from .iprocessable import IProcessable


class ASTListSetVar(IProcessable):
    def __init__(self, name: IGetter, index: IGetter, right: IGetter):
        self.name: IGetter = name
        self.index: IGetter = index
        self.right: IGetter = right

    def process(self, declarations: Dict[str, CodeVar], stack: Stack, out: CodeBuffer) -> None:
        var: CodeVar = self.name.get_var(declarations)
        assert isinstance(var.type, StringCodeType)
        a = ASTCase(self.index, [
            (i, [ASTSetVar([IndexGetter(self.name, i)], self.right)])
            for i in range(var.type.len_)
        ])
        out.write(a)
