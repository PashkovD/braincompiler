from typing import Dict, Tuple

from .code_buffer import CodeBuffer
from .code_getters import VarGetter, IndexGetter
from .code_stack import Stack
from .code_types import IntCodeType, StringCodeType
from .code_var import CodeVar
from .goto import Goto
from .ideclaration import IDeclaration
from .iprocessable import IProcessable
from .util import bf_add


class ASTIntDeclaration(IProcessable, IDeclaration):
    def __init__(self, name: str, start: int):
        if not isinstance(start, int):
            raise Exception(f"Incorrect type of start value of {name}")
        self.start: int
        super(ASTIntDeclaration, self).__init__(name, start)

    def process(self, declarations: Dict[str, CodeVar], stack: Stack, out: CodeBuffer) -> None:
        out.write(Goto(VarGetter(self.name)))
        out.write("[-]")
        out.write(bf_add(self.start))

    def key(self, pos: int) -> Tuple[str, CodeVar]:
        return self.name, CodeVar(pos, IntCodeType())


class ASTStringDeclaration(IProcessable, IDeclaration):
    def __init__(self, name: str, start: bytes):
        if not isinstance(start, bytes):
            raise Exception(f"Incorrect type of start value of {name}")
        self.start: bytes
        super(ASTStringDeclaration, self).__init__(name, start)

    def __str__(self):
        return f"string {self.name}={repr(self.start)}"

    def process(self, declarations: Dict[str, CodeVar], stack: Stack, out: CodeBuffer) -> None:
        for i, f in enumerate(self.start):
            out.write(Goto(IndexGetter(VarGetter(self.name), i)))
            out.write("[-]")
            out.write(bf_add(f))

    def key(self, pos: int) -> Tuple[str, CodeVar]:
        return self.name, CodeVar(pos, StringCodeType(len(self.start)))
