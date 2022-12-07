from typing import Dict, List

from .code_buffer import CodeBuffer
from .code_getters import IGetter
from .code_stack import Stack
from .code_var import CodeVar
from .goto import Goto
from .iprocessable import IProcessable


class ASTAssembler(IProcessable):
    def __init__(self, code: str):
        self.code: str = code

    def __str__(self):
        return f"asm({repr(self.code)})"

    def process(self, declarations: Dict[str, CodeVar], stack: Stack, out: CodeBuffer) -> None:
        out.write(self.code)


class ASTGoto(IProcessable):
    def __init__(self, name: IGetter):
        self.name: IGetter = name

    def __str__(self):
        return f"goto {self.name}"

    def process(self, declarations: Dict[str, CodeVar], stack: Stack, out: CodeBuffer) -> None:
        out.write(Goto(self.name))


class ASTOut(IProcessable):
    def __init__(self, name: IGetter):
        self.name: IGetter = name

    def __str__(self):
        return f"out {self.name}"

    def process(self, declarations: Dict[str, CodeVar], stack: Stack, out: CodeBuffer) -> None:
        out.write(Goto(self.name))
        out.write(".")


class ASTIn(IProcessable):
    def __init__(self, name: IGetter):
        self.name: IGetter = name

    def __str__(self):
        return f"out {self.name}"

    def process(self, declarations: Dict[str, CodeVar], stack: Stack, out: CodeBuffer) -> None:
        out.write(Goto(self.name))
        out.write(",")


class ASTWhile(IProcessable):
    def __init__(self, test_var: IGetter, code: List[IProcessable]):
        self.test_var: IGetter = test_var
        self.code: List[IProcessable] = code
        assert all(isinstance(i, IProcessable) for i in self.code)

    def __str__(self):
        return f"while({self.test_var})"

    def process(self, declarations: Dict[str, CodeVar], stack: Stack, out: CodeBuffer) -> None:
        out.write(Goto(self.test_var))
        out.write("[")
        for i in self.code:
            out.write(i)
        out.write(Goto(self.test_var))
        out.write("]")
