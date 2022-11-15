from typing import Dict, List, Union, Tuple

from .code_getters import IndexGetter, VarGetter
from .code_types import StringCodeType
from .code_var import CodeVar
from .goto import Goto
from .ideclaration import IDeclaration


class Stack(IDeclaration):
    def __init__(self, name: str):
        super(Stack, self).__init__(name, 0)
        self.size: int = 0
        self.current: int = 0

    def process(self, declarations: Dict[str, CodeVar], stack) -> List[Union[Goto, str]]:
        data: List[Union[Goto, str]] = []
        for i in range(self.size):
            data += [Goto(IndexGetter(VarGetter(self.name), i)), "[-]"]
        return data

    def key(self, pos: int) -> Tuple[str, CodeVar]:
        return self.name, CodeVar(pos, StringCodeType(self.size))

    def push(self) -> IndexGetter:
        self.current += 1
        self.size = max(self.size, self.current)
        return IndexGetter(VarGetter(self.name), self.current - 1)

    def pop(self, name: IndexGetter):
        self.current -= 1
        if name != IndexGetter(VarGetter(self.name), self.current):
            raise Exception(f"Incorrect var in stack {repr(name)}")
        if self.current < 0:
            raise Exception(f"Incorrect var in stack {repr(name)}")
