from .icode_type import ICodeType


class CodeVar:
    def __init__(self, pos: int, type_: ICodeType):
        self.pos: int = pos
        self.type: ICodeType = type_

    def get_size(self) -> int:
        return self.type.get_size()
