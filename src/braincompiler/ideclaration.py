from typing import Dict, Tuple

from .code_var import CodeVar
from .ibuffer import IBuffer


class IDeclaration:
    def __init__(self, name: str, start):
        self.start = start
        self.name: str = name

    def process(self, declarations: Dict[str, CodeVar], stack, out: IBuffer) -> None:
        raise Exception

    def key(self, pos: int) -> Tuple[str, CodeVar]:
        raise Exception
