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


class Stack(IDeclaration):
    def __init__(self, name: str):
        super(Stack, self).__init__(name, 0)
        self.size: int = 0
        self.current: int = 0

    def process(self) -> List[Union[Goto, str]]:
        data: List[Union[Goto, str]] = []
        for i in range(self.size):
            data += [Goto(f"{self.name}[{i}]"), "[-]"]
        return data

    def keys(self, pos: int) -> Tuple[Dict[str, int], int]:
        data: Dict[str, int] = {}
        for i in range(self.size):
            data[f"{self.name}[{i}]"] = pos + i
        return data, self.size

    def push(self) -> str:
        self.current += 1
        self.size = max(self.size, self.current)
        return f"{self.name}[{self.current - 1}]"

    def pop(self, name: str):
        self.current -= 1
        if name != f"{self.name}[{self.current}]":
            raise Exception(f"Incorrect var in stack {repr(name)}")
        if self.current < 0:
            raise Exception(f"Incorrect var in stack {repr(name)}")


class IProcessable:
    def process(self, declarations: Dict[str, IDeclaration], stack: Stack) -> List[Union[Goto, str]]:
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
    def __init__(self, name: str, start: bytes):
        if not isinstance(start, bytes):
            raise Exception(f"Incorrect type of start value of {name}")
        self.start: bytes
        super(ASTStringDeclaration, self).__init__(name, start)

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

    def process(self, declarations: Dict[str, IDeclaration], stack: Stack) -> List[Union[Goto, str]]:
        return [self.code]


class ASTGoto(IProcessable):
    def __init__(self, name: str):
        self.name: str = name

    def __str__(self):
        return f"goto {self.name}"

    def process(self, declarations: Dict[str, IDeclaration], stack: Stack) -> List[Union[Goto, str]]:
        return [Goto(self.name)]


class ASTOut(IProcessable):
    def __init__(self, name: str):
        self.name: str = name

    def __str__(self):
        return f"out {self.name}"

    def process(self, declarations: Dict[str, IDeclaration], stack: Stack) -> List[Union[Goto, str]]:
        return [Goto(self.name), "."]


class ASTIn(IProcessable):
    def __init__(self, name: str):
        self.name: str = name

    def __str__(self):
        return f"out {self.name}"

    def process(self, declarations: Dict[str, IDeclaration], stack: Stack) -> List[Union[Goto, str]]:
        return [Goto(self.name), ","]


class ASTIaddInt(IProcessable):
    def __init__(self, names: List[str], num: int):
        self.names: List[str] = names
        self.num: int = num

    def __str__(self):
        return f"{str(self.names)[1:-1]} += {self.num}"

    def process(self, declarations: Dict[str, IDeclaration], stack: Stack) -> List[Union[Goto, str]]:
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

    def process(self, declarations: Dict[str, IDeclaration], stack: Stack) -> List[Union[Goto, str]]:
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

    def process(self, declarations: Dict[str, IDeclaration], stack: Stack) -> List[Union[Goto, str]]:
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

    def process(self, declarations: Dict[str, IDeclaration], stack: Stack) -> List[Union[Goto, str]]:
        data = []
        copy_var = stack.push()
        data += [Goto(copy_var), "[-]"]
        data += [Goto(self.right), "[", "-"]
        for i in self.names:
            data += [Goto(i), "+"]
        data += [Goto(copy_var), "+"]
        data += [Goto(self.right), "]"]

        data += [Goto(copy_var), "[-", Goto(self.right), "+", Goto(copy_var), "]"]
        stack.pop(copy_var)
        return data


class ASTIsubVar(IProcessable):
    def __init__(self, names: List[str], right: str):
        self.names: List[str] = names
        self.right: str = right

    def __str__(self):
        return f"{str(self.names)[1:-1]} -= {self.right}"

    def process(self, declarations: Dict[str, IDeclaration], stack: Stack) -> List[Union[Goto, str]]:
        data = []
        copy_var = stack.push()
        data += [Goto(copy_var), "[-]"]
        data += [Goto(self.right), "[", "-"]
        for i in self.names:
            data += [Goto(i), "-"]
        data += [Goto(copy_var), "+"]
        data += [Goto(self.right), "]"]

        data += [Goto(copy_var), "[-", Goto(self.right), "+", Goto(copy_var), "]"]
        stack.pop(copy_var)
        return data


class ASTSetVar(IProcessable):
    def __init__(self, names: List[str], right: str):
        self.names: List[str] = names
        self.right: str = right

    def __str__(self):
        return f"{str(self.names)[1:-1]} = {self.right}"

    def process(self, declarations: Dict[str, IDeclaration], stack: Stack) -> List[Union[Goto, str]]:
        data = []
        for i in self.names:
            data += [Goto(i), "[-]"]

        copy_var = stack.push()
        data += [Goto(copy_var), "[-]"]
        data += [Goto(self.right), "[", "-"]
        for i in self.names:
            data += [Goto(i), "+"]
        data += [Goto(copy_var), "+"]
        data += [Goto(self.right), "]"]

        data += [Goto(copy_var), "[-", Goto(self.right), "+", Goto(copy_var), "]"]
        stack.pop(copy_var)
        return data


class ASTWhile(IProcessable):
    def __init__(self, test_var: str, code: List[IProcessable]):
        self.test_var: str = test_var
        self.code: List[IProcessable] = code
        assert all(isinstance(i, IProcessable) for i in self.code)

    def __str__(self):
        return f"while({self.test_var})"

    def process(self, declarations: Dict[str, IDeclaration], stack: Stack) -> List[Union[Goto, str]]:
        data = []
        data += [Goto(self.test_var), "["]
        for i in self.code:
            data += i.process(declarations, stack)
        data += [Goto(self.test_var), "]"]
        return data


class ASTIf(IProcessable):
    def __init__(self, test_var: str, code: List[IProcessable]):
        self.test_var: str = test_var
        self.code: List[IProcessable] = code

    def __str__(self):
        return f"if({self.test_var})"

    def process(self, declarations: Dict[str, IDeclaration], stack: Stack) -> List[Union[Goto, str]]:
        data = []
        copy_var = stack.push()
        data += ASTSetVar([copy_var], self.test_var).process(declarations, stack)
        data += ASTWhile(copy_var, self.code + [ASTSetInt([copy_var], 0)]).process(declarations, stack)
        stack.pop(copy_var)
        return data


class ASTIfElif(IProcessable):
    def __init__(self, data: List[Tuple[str, List[IProcessable]]], code_else: List[IProcessable] = None):
        self.data: List[Tuple[str, List[IProcessable]]] = data
        self.code_else: List[IProcessable] = code_else

    def __str__(self):
        return f"if({self.data[0][0]})" + \
               "".join(f"elif({i[0]})" for i in self.data) + \
               f"else" if self.code_else is not None else ""

    def process(self, declarations: Dict[str, IDeclaration], stack: Stack) -> List[Union[Goto, str]]:
        data = []
        else_flag = stack.push()
        data += ASTSetInt([else_flag], 1).process(declarations, stack)
        data += ASTIf(self.data[0][0], self.data[0][1] + [ASTSetInt([else_flag], 0)]).process(declarations, stack)
        for i in self.data[1:]:
            data += ASTIf(
                else_flag,
                [ASTIf(i[0], i[1] + [ASTSetInt([else_flag], 0)])]
            ).process(declarations, stack)
        if self.code_else is not None:
            data += ASTIf(else_flag, self.code_else).process(declarations, stack)
        stack.pop(else_flag)
        return data


class ASTCase(IProcessable):
    def __init__(self, test_var: str, code: List[Tuple[int, List[IProcessable]]]):
        self.test_var: str = test_var
        self.code: List[Tuple[int, List[IProcessable]]] = code

    def process(self, declarations: Dict[str, IDeclaration], stack: Stack) -> List[Union[Goto, str]]:
        data: List[Union[Goto, str]] = []
        if len(self.code) != 0:
            copy_var = stack.push()
            data += ASTSetVar([copy_var], self.test_var).process(declarations, stack)
            last = 0
            for i in self.code:
                data += ASTIsubInt([copy_var], i[0] - last).process(declarations, stack)
                data += ASTIfElif([(copy_var, [])], code_else=i[1]).process(declarations, stack)
                last = i[0]

            stack.pop(copy_var)
        return data


class ASTIdivVar(IProcessable):
    def __init__(self, names: List[str], right: str):
        self.names: List[str] = names
        self.right: str = right

    def process(self, declarations: Dict[str, IDeclaration], stack: Stack) -> List[Union[Goto, str]]:
        data: List[Union[Goto, str]] = []
        for left in self.names:
            work = stack.push()
            data += ASTSetInt([work], 1).process(declarations, stack)
            counter = stack.push()
            data += ASTSetInt([counter], 0).process(declarations, stack)
            left_var = stack.push()
            data += ASTSetVar([left_var], left).process(declarations, stack)
            right_var = stack.push()

            data += ASTWhile(work, [
                ASTSetVar([right_var], self.right),
                ASTWhile(right_var, [
                    ASTIfElif([(left_var, [])], code_else=[
                        ASTSetInt([work], 0),
                        ASTSetInt([left_var, right_var], 1),
                    ]),
                    ASTIsubInt([left_var, right_var], 1),
                ]),
                ASTIaddInt([counter], 1),
            ]).process(declarations, stack)
            data += ASTIsubInt([counter], 1).process(declarations, stack)
            data += ASTSetVar([left], counter).process(declarations, stack)
            stack.pop(right_var)
            stack.pop(left_var)
            stack.pop(counter)
            stack.pop(work)
        return data


class ASTImodVar(IProcessable):
    def __init__(self, names: List[str], right: str):
        self.names: List[str] = names
        self.right: str = right

    def process(self, declarations: Dict[str, IDeclaration], stack: Stack) -> List[Union[Goto, str]]:
        data: List[Union[Goto, str]] = []
        for left in self.names:
            work = stack.push()
            data += ASTSetInt([work], 1).process(declarations, stack)
            left_var = stack.push()
            data += ASTSetVar([left_var], left).process(declarations, stack)
            right_var = stack.push()

            data += ASTWhile(work, [
                ASTSetVar([right_var], self.right),
                ASTWhile(right_var, [
                    ASTIfElif([(left_var, [])], code_else=[
                        ASTSetInt([work], 0),
                        ASTSetVar([left], self.right),
                        ASTIsubVar([left], right_var),
                        ASTSetInt([left_var, right_var], 1),
                    ]),
                    ASTIsubInt([left_var, right_var], 1),
                ]),
            ]).process(declarations, stack)
            stack.pop(right_var)
            stack.pop(left_var)
            stack.pop(work)
        return data


class ASTIdivInt(IProcessable):
    def __init__(self, names: List[str], num: int):
        self.names: List[str] = names
        self.num: int = num

    def process(self, declarations: Dict[str, IDeclaration], stack: Stack) -> List[Union[Goto, str]]:
        data: List[Union[Goto, str]] = []
        for left in self.names:
            work = stack.push()
            data += ASTSetInt([work], 1).process(declarations, stack)
            counter = stack.push()
            data += ASTSetInt([counter], 0).process(declarations, stack)
            left_var = stack.push()
            data += ASTSetVar([left_var], left).process(declarations, stack)
            right_var = stack.push()

            data += ASTWhile(work, [
                ASTSetInt([right_var], self.num),
                ASTWhile(right_var, [
                    ASTIfElif([(left_var, [])], code_else=[
                        ASTSetInt([work], 0),
                        ASTSetInt([left_var, right_var], 1),
                    ]),
                    ASTIsubInt([left_var, right_var], 1),
                ]),
                ASTIaddInt([counter], 1),
            ]).process(declarations, stack)
            data += ASTIsubInt([counter], 1).process(declarations, stack)
            data += ASTSetVar([left], counter).process(declarations, stack)
            stack.pop(right_var)
            stack.pop(left_var)
            stack.pop(counter)
            stack.pop(work)
        return data


class ASTImodInt(IProcessable):
    def __init__(self, names: List[str], num: int):
        self.names: List[str] = names
        self.num: int = num

    def process(self, declarations: Dict[str, IDeclaration], stack: Stack) -> List[Union[Goto, str]]:
        data: List[Union[Goto, str]] = []
        for left in self.names:
            work = stack.push()
            data += ASTSetInt([work], 1).process(declarations, stack)
            left_var = stack.push()
            data += ASTSetVar([left_var], left).process(declarations, stack)
            right_var = stack.push()

            data += ASTWhile(work, [
                ASTSetInt([right_var], self.num),
                ASTWhile(right_var, [
                    ASTIfElif([(left_var, [])], code_else=[
                        ASTSetInt([work], 0),
                        ASTSetInt([left], self.num),
                        ASTIsubVar([left], right_var),
                        ASTSetInt([left_var, right_var], 1),
                    ]),
                    ASTIsubInt([left_var, right_var], 1),
                ]),
            ]).process(declarations, stack)
            stack.pop(right_var)
            stack.pop(left_var)
            stack.pop(work)
        return data


class ASTImulVar(IProcessable):
    def __init__(self, names: List[str], right: str):
        self.names: List[str] = names
        self.right: str = right

    def process(self, declarations: Dict[str, IDeclaration], stack: Stack) -> List[Union[Goto, str]]:
        data: List[Union[Goto, str]] = []
        for left in self.names:
            copy_var = stack.push()
            copy_var2 = stack.push()
            data += ASTSetVar([copy_var], left).process(declarations, stack)
            data += ASTSetVar([copy_var2], self.right).process(declarations, stack)
            data += ASTSetInt([left], 0).process(declarations, stack)
            data += ASTWhile(copy_var2, [
                ASTIsubInt([copy_var2], 1),
                ASTIaddVar([left], copy_var),
            ]).process(declarations, stack)
            stack.pop(copy_var2)
            stack.pop(copy_var)
        return data


class ASTImulInt(IProcessable):
    def __init__(self, names: List[str], num: int):
        self.names: List[str] = names
        self.num: int = num

    def process(self, declarations: Dict[str, IDeclaration], stack: Stack) -> List[Union[Goto, str]]:
        if self.num == 0:
            return ASTSetInt(self.names, self.num).process(declarations, stack)
        data: List[Union[Goto, str]] = []
        if abs(self.num) >= 16:
            copy_var = stack.push()
            data += ASTSetInt([copy_var], self.num).process(declarations, stack)
            data += ASTImulVar(self.names, copy_var).process(declarations, stack)
            stack.pop(copy_var)
            return data

        for left in self.names:
            copy_var = stack.push()
            data += ASTSetVar([copy_var], left).process(declarations, stack)
            data += ASTIaddVar([left], copy_var).process(declarations, stack) * (self.num - 1)
            stack.pop(copy_var)
        return data


class ASTIlshiftInt(IProcessable):
    def __init__(self, names: List[str], num: int):
        self.names: List[str] = names
        self.num: int = num

    def process(self, declarations: Dict[str, IDeclaration], stack: Stack) -> List[Union[Goto, str]]:
        if self.num == 0:
            return ASTSetInt(self.names, 0).process(declarations, stack)
        return ASTImulInt(self.names, 2 ** self.num).process(declarations, stack)


class ASTIrshiftInt(IProcessable):
    def __init__(self, names: List[str], num: int):
        self.names: List[str] = names
        self.num: int = num

    def process(self, declarations: Dict[str, IDeclaration], stack: Stack) -> List[Union[Goto, str]]:
        if self.num == 0:
            return []
        return ASTIdivInt(self.names, 2 ** self.num).process(declarations, stack)


class ASTFile:
    def __init__(self):
        self.declarations: Dict[str, IDeclaration] = {}
        self.code: List[IProcessable] = []

    def process(self) -> Tuple[List[Union[Goto, str]], Dict[str, IDeclaration]]:
        code: List[Union[Goto, str]] = []
        declarations: List[Union[Goto, str]] = []
        stack: Stack = Stack("__stack")

        for i in self.code:
            code += i.process(self.declarations, stack)

        declarations += stack.process()

        for i in self.declarations.values():
            declarations += i.process()
        if stack.current != 0:
            raise Exception("Stack not empty at end")
        return declarations + code, {stack.name: stack} | self.declarations
