from typing import Dict

from .code_stack import Stack
from .code_var import CodeVar
from .ibuffer import IBuffer


class IProcessable:
    def process(self, declarations: Dict[str, CodeVar], stack: Stack, out: IBuffer) -> None:
        raise Exception
