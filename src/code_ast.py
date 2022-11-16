from collections import OrderedDict
from itertools import chain
from typing import List, Union, Tuple, Dict

from .code_buffer import CodeBuffer
from .code_stack import Stack
from .code_var import CodeVar
from .goto import Goto
from .ideclaration import IDeclaration
from .iprocessable import IProcessable


class ASTFile:
    def __init__(self):
        self.declarations: Dict[str, IDeclaration] = OrderedDict()
        self.code: List[IProcessable] = []

    def process(self) -> Tuple[List[Union[Goto, str]], Dict[str, CodeVar]]:
        decls: Dict[str, CodeVar] = {}
        stack: Stack = Stack("__stack")

        code: CodeBuffer = CodeBuffer(decls, stack)
        declarations_code: CodeBuffer = CodeBuffer(decls, stack)

        for i in self.code:
            code.write(i)

        for i in chain([stack], self.declarations.values()):
            i.process(decls, stack, declarations_code)

        pos = 0
        for i in chain([stack], self.declarations.values()):
            name, var = i.key(pos)
            decls[name] = var
            pos += var.get_size()

        if stack.current != 0:
            raise Exception("Stack not empty at end")

        return declarations_code.queue + code.queue, decls
