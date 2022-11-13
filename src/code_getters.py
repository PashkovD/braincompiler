from typing import Dict

from code_types import StringCodeType
from code_var import CodeVar


class IGetter:
    def get_var(self, declarations: Dict[str, CodeVar]) -> CodeVar:
        raise Exception


class VarGetter(IGetter):
    def __init__(self, name: str):
        self.name: str = name

    def get_var(self, declarations: Dict[str, CodeVar]) -> CodeVar:
        return declarations[self.name]


class IndexGetter(IGetter):
    def __init__(self, getter: IGetter, index: int):
        self.getter: IGetter = getter
        self.index: int = index

    def get_var(self, declarations: Dict[str, CodeVar]) -> CodeVar:
        var = self.getter.get_var(declarations)
        assert isinstance(var.type, StringCodeType), "Getting element from not array"
        return var.type.get_item(var, self.index)
