from typing import List, Union

from goto import Goto
from util import bf_add


class ASTDeclaration:
    def __init__(self, name: str, default: int):
        self.default: int = default
        self.name: str = name

    def __str__(self):
        return f"int {self.name}={self.default}"

    def process(self) -> List[Union[Goto, str]]:
        return [Goto(self.name), "[-]", bf_add(self.default)]


class IProcessable:
    def process(self, declarations: List[ASTDeclaration]) -> List[Union[Goto, str]]:
        raise Exception


class ASTAssembler(IProcessable):
    def __init__(self, code: str):
        self.code: str = code

    def __str__(self):
        return f"asm({repr(self.code)})"

    def process(self, declarations: List[ASTDeclaration]) -> List[Union[Goto, str]]:
        return [self.code]


class ASTGoto(IProcessable):
    def __init__(self, name: str):
        self.name: str = name

    def __str__(self):
        return f"goto {self.name}"

    def process(self, declarations: List[ASTDeclaration]) -> List[Union[Goto, str]]:
        return [Goto(self.name)]


class ASTOut(IProcessable):
    def __init__(self, name: str):
        self.name: str = name

    def __str__(self):
        return f"out {self.name}"

    def process(self, declarations: List[ASTDeclaration]) -> List[Union[Goto, str]]:
        return [Goto(self.name), "."]


class ASTIn(IProcessable):
    def __init__(self, name: str):
        self.name: str = name

    def __str__(self):
        return f"out {self.name}"

    def process(self, declarations: List[ASTDeclaration]) -> List[Union[Goto, str]]:
        return [Goto(self.name), ","]


class ASTFile:
    def __init__(self):
        self.declarations: List[ASTDeclaration] = []
        self.code: List[IProcessable] = []

    def process(self) -> List[Union[Goto, str]]:
        data: List[Union[Goto, str]] = []
        for i in self.declarations:
            data.extend(i.process())

        for i in self.code:
            data.extend(i.process(self.declarations))
        return data
