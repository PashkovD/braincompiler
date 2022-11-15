from typing import Dict, Union, List

from .code_stack import Stack
from .code_var import CodeVar
from .goto import Goto
from .ibuffer import IBuffer
from .iprocessable import IProcessable


class CodeBuffer(IBuffer):
    def __init__(self, declarations: Dict[str, CodeVar], stack: Stack):
        self.declarations: Dict[str, CodeVar] = declarations
        self.stack: Stack = stack

        self.queue: List[Union[Goto, str]] = []

    def write(self, data: Union[Goto, str, IProcessable]) -> None:
        if isinstance(data, IProcessable):
            data.process(self.declarations, self.stack, self)
            return

        self.queue.append(data)
