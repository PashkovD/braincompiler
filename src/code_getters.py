from typing import Dict

from .code_types import StringCodeType
from .code_var import CodeVar


class IGetter:
    def get_var(self, declarations: Dict[str, CodeVar]) -> CodeVar:
        raise Exception

    def __eq__(self, other: "IGetter") -> bool:
        return self is other


class VarGetter(IGetter):
    def __init__(self, name: str):
        self.name: str = name

    def get_var(self, declarations: Dict[str, CodeVar]) -> CodeVar:
        return declarations[self.name]

    def __eq__(self, other: IGetter) -> bool:
        if not isinstance(other, type(self)):
            return False
        return self.name == other.name


class IndexGetter(IGetter):
    def __init__(self, getter: IGetter, index: int):
        self.getter: IGetter = getter
        self.index: int = index

    def get_var(self, declarations: Dict[str, CodeVar]) -> CodeVar:
        var = self.getter.get_var(declarations)
        assert isinstance(var.type, StringCodeType), "Getting element from not array"
        return var.type.get_item(var, self.index)

    def __eq__(self, other: IGetter) -> bool:
        if not isinstance(other, type(self)):
            return False
        return self.getter == other.getter and self.index == other.index
