from typing import Dict, List, Union

from .code_stack import Stack
from .code_var import CodeVar
from .goto import Goto


class IProcessable:
    def process(self, declarations: Dict[str, CodeVar], stack: Stack) -> List[Union[Goto, str]]:
        raise Exception
