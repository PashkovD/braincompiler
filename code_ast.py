from typing import List, Union, Tuple, Dict

from .goto import Goto
from .util import bf_add


class IDeclaration:
    def __init__(self, name: str, start):
        self.start = start
        self.name: str = name

    def process(self) -> List[Union[Goto, str]]:
        raise Exception

    def keys(self, pos: int) -> Tuple[Dict[str, int], int]:
        raise Exception


class IProcessable:
    def process(self, declarations: Dict[str, IDeclaration]) -> List[Union[Goto, str]]:
        raise Exception


class ASTIntDeclaration(IDeclaration):
    def __init__(self, name: str, start: int):
        if not isinstance(start, int):
            raise Exception(f"Incorrect type of start value of {name}")
        self.start: int
        super(ASTIntDeclaration, self).__init__(name, start)

    def __str__(self):
        return f"int {self.name}={self.start}"

    def process(self) -> List[Union[Goto, str]]:
        return [Goto(self.name), "[-]", bf_add(self.start)]

    def keys(self, pos: int) -> Tuple[Dict[str, int], int]:
        return {self.name: pos}, 1


class ASTStringDeclaration(IDeclaration):
    def __init__(self, name: str, start: str):
        if not isinstance(start, str):
            raise Exception(f"Incorrect type of start value of {name}")
        self.start: bytes
        super(ASTStringDeclaration, self).__init__(name, bytes(start, "utf-8"))

    def __str__(self):
        return f"string {self.name}={repr(self.start)}"

    def process(self) -> List[Union[Goto, str]]:
        data: List[Union[Goto, str]] = []
        for i, f in enumerate(self.start):
            data += [Goto(f"{self.name}[{i}]"), "[-]", bf_add(f)]
        return data

    def keys(self, pos: int) -> Tuple[Dict[str, int], int]:
        data: Dict[str, int] = {
            self.name: pos
        }
        for i in range(len(self.start)):
            data[f"{self.name}[{i}]"] = pos + i
        return data, len(self.start)


class ASTAssembler(IProcessable):
    def __init__(self, code: str):
        self.code: str = code

    def __str__(self):
        return f"asm({repr(self.code)})"

    def process(self, declarations: Dict[str, IDeclaration]) -> List[Union[Goto, str]]:
        return [self.code]


class ASTGoto(IProcessable):
    def __init__(self, name: str):
        self.name: str = name

    def __str__(self):
        return f"goto {self.name}"

    def process(self, declarations: Dict[str, IDeclaration]) -> List[Union[Goto, str]]:
        return [Goto(self.name)]


class ASTOut(IProcessable):
    def __init__(self, name: str):
        self.name: str = name

    def __str__(self):
        return f"out {self.name}"

    def process(self, declarations: Dict[str, IDeclaration]) -> List[Union[Goto, str]]:
        return [Goto(self.name), "."]


class ASTIn(IProcessable):
    def __init__(self, name: str):
        self.name: str = name

    def __str__(self):
        return f"out {self.name}"

    def process(self, declarations: Dict[str, IDeclaration]) -> List[Union[Goto, str]]:
        return [Goto(self.name), ","]


class ASTIaddInt(IProcessable):
    def __init__(self, names: List[str], num: int):
        self.names: List[str] = names
        self.num: int = num

    def __str__(self):
        return f"{str(self.names)[1:-1]} += {self.num}"

    def process(self, declarations: Dict[str, IDeclaration]) -> List[Union[Goto, str]]:
        data = []
        for i in self.names:
            data += [Goto(i), bf_add(self.num)]
        return data


class ASTIsubInt(IProcessable):
    def __init__(self, names: List[str], num: int):
        self.names: List[str] = names
        self.num: int = num

    def __str__(self):
        return f"{str(self.names)[1:-1]} -= {self.num}"

    def process(self, declarations: Dict[str, IDeclaration]) -> List[Union[Goto, str]]:
        data = []
        for i in self.names:
            data += [Goto(i), bf_add(-self.num)]
        return data


class ASTSetInt(IProcessable):
    def __init__(self, names: List[str], num: int):
        self.names: List[str] = names
        self.num: int = num

    def __str__(self):
        return f"{str(self.names)[1:-1]} = {self.num}"

    def process(self, declarations: Dict[str, IDeclaration]) -> List[Union[Goto, str]]:
        data = []
        for i in self.names:
            data += [Goto(i), "[-]", bf_add(self.num)]
        return data


class ASTIaddVar(IProcessable):
    def __init__(self, names: List[str], right: str):
        self.names: List[str] = names
        self.right: str = right

    def __str__(self):
        return f"{str(self.names)[1:-1]} += {self.right}"

    def process(self, declarations: Dict[str, IDeclaration]) -> List[Union[Goto, str]]:
        data = []
        data += [Goto(self.right), "[", "-"]
        for i in self.names:
            data += [Goto(i), "+"]

        data += [Goto(self.right), "]"]
        return data


class ASTIsubVar(IProcessable):
    def __init__(self, names: List[str], right: str):
        self.names: List[str] = names
        self.right: str = right

    def __str__(self):
        return f"{str(self.names)[1:-1]} -= {self.right}"

    def process(self, declarations: Dict[str, IDeclaration]) -> List[Union[Goto, str]]:
        data = []
        data += [Goto(self.right), "[", "-"]
        for i in self.names:
            data += [Goto(i), "-"]

        data += [Goto(self.right), "]"]
        return data


class ASTSetVar(IProcessable):
    def __init__(self, names: List[str], right: str):
        self.names: List[str] = names
        self.right: str = right

    def __str__(self):
        return f"{str(self.names)[1:-1]} = {self.right}"

    def process(self, declarations: Dict[str, IDeclaration]) -> List[Union[Goto, str]]:
        data = []
        for i in self.names:
            data += [Goto(i), "[-]"]

        data += [Goto(self.right), "[", "-"]
        for i in self.names:
            data += [Goto(i), "+"]

        data += [Goto(self.right), "]"]
        return data


class ASTWhile(IProcessable):
    def __init__(self, test_var: str, code: List[IProcessable]):
        self.test_var: str = test_var
        self.code: List[IProcessable] = code

    def __str__(self):
        return f"while({self.test_var})"

    def process(self, declarations: Dict[str, IDeclaration]) -> List[Union[Goto, str]]:
        data = []
        data += [Goto(self.test_var), "["]
        for i in self.code:
            data += i.process(declarations)
        data += [Goto(self.test_var), "]"]
        return data


class ASTIf(IProcessable):
    def __init__(self, test_var: str, code: List[IProcessable]):
        self.test_var: str = test_var
        self.code: List[IProcessable] = code

    def __str__(self):
        return f"if({self.test_var})"

    def process(self, declarations: Dict[str, IDeclaration]) -> List[Union[Goto, str]]:
        data = []
        data += [Goto(self.test_var), "["]
        for i in self.code:
            data += i.process(declarations)
        data += ASTSetVar(["__copy_var"], self.test_var).process(declarations)
        data += [Goto(self.test_var), "]"]
        data += ASTSetVar([self.test_var], "__copy_var").process(declarations)
        return data


class ASTIfElif(IProcessable):
    def __init__(self, data: List[Tuple[str, List[IProcessable]]], code_else: List[IProcessable] = None):
        self.data: List[Tuple[str, List[IProcessable]]] = data
        self.code_else: List[IProcessable] = code_else

    def __str__(self):
        return f"if({self.data[0][0]})" + \
               "".join(f"elif({i[0]})" for i in self.data) + \
               f"else" if self.code_else is not None else ""

    def process(self, declarations: Dict[str, IDeclaration]) -> List[Union[Goto, str]]:
        data = []
        data += ASTSetInt(["__else_flag"], 1).process(declarations)
        data += ASTIf(self.data[0][0], self.data[0][1] + [ASTSetInt(["__else_flag"], 0)]).process(declarations)
        for i in self.data[1:]:
            data += ASTIf("__else_flag",
                          [ASTIf(i[0], i[1] + [ASTSetInt(["__else_flag"], 0)])]
                          ).process(declarations)
        if self.code_else is not None:
            data += ASTIf("__else_flag", self.code_else + [ASTSetInt(["__else_flag"], 0)]).process(declarations)
        return data


class ASTFile:
    def __init__(self):
        self.declarations: Dict[str, IDeclaration] = {}
        self.code: List[IProcessable] = []

    def process(self) -> List[Union[Goto, str]]:
        data: List[Union[Goto, str]] = []
        for i in self.declarations.values():
            data += i.process()

        for i in self.code:
            data += i.process(self.declarations)
        return data
