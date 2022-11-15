from typing import Dict, List, Union, Tuple

from .code_var import CodeVar
from .goto import Goto


class IDeclaration:
    def __init__(self, name: str, start):
        self.start = start
        self.name: str = name

    def process(self, declarations: Dict[str, CodeVar], stack) -> List[Union[Goto, str]]:
        raise Exception

    def key(self, pos: int) -> Tuple[str, CodeVar]:
        raise Exception
