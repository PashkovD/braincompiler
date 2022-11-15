from .code_var import CodeVar
from .icode_type import ICodeType


class IntCodeType(ICodeType):
    def get_size(self) -> int:
        return 1


class StringCodeType(ICodeType):
    def __init__(self, len_: int):
        self.len_: int = len_

    def get_size(self) -> int:
        return IntCodeType().get_size() * self.len_

    def get_item(self, var: CodeVar, n: int) -> CodeVar:
        assert n < self.len_, "index not in string"
        return CodeVar(var.pos + IntCodeType().get_size() * n, IntCodeType())
