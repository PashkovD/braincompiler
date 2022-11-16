from collections import OrderedDict
from itertools import chain
from typing import List, Union, Tuple, Dict

from .base_ast import ASTWhile
from .code_buffer import CodeBuffer
from .code_getters import IGetter
from .code_stack import Stack
from .code_var import CodeVar
from .goto import Goto
from .ideclaration import IDeclaration
from .iprocessable import IProcessable
from .util import bf_add


class ASTIaddInt(IProcessable):
    def __init__(self, names: List[IGetter], num: int):
        self.names: List[IGetter] = names
        self.num: int = num

    def __str__(self):
        return f"{str(self.names)[1:-1]} += {self.num}"

    def process(self, declarations: Dict[str, CodeVar], stack: Stack, out: CodeBuffer) -> None:
        for i in self.names:
            out.write(Goto(i))
            out.write(bf_add(self.num))


class ASTIsubInt(IProcessable):
    def __init__(self, names: List[IGetter], num: int):
        self.names: List[IGetter] = names
        self.num: int = num

    def __str__(self):
        return f"{str(self.names)[1:-1]} -= {self.num}"

    def process(self, declarations: Dict[str, CodeVar], stack: Stack, out: CodeBuffer) -> None:
        for i in self.names:
            out.write(Goto(i))
            out.write(bf_add(-self.num))


class ASTSetInt(IProcessable):
    def __init__(self, names: List[IGetter], num: int):
        self.names: List[IGetter] = names
        self.num: int = num

    def __str__(self):
        return f"{str(self.names)[1:-1]} = {self.num}"

    def process(self, declarations: Dict[str, CodeVar], stack: Stack, out: CodeBuffer) -> None:
        for i in self.names:
            out.write(Goto(i))
            out.write("[-]")

        out.write(ASTIaddInt(self.names, self.num))


class ASTIaddVar(IProcessable):
    def __init__(self, names: List[IGetter], right: IGetter):
        self.names: List[IGetter] = names
        self.right: IGetter = right

    def __str__(self):
        return f"{str(self.names)[1:-1]} += {self.right}"

    def process(self, declarations: Dict[str, CodeVar], stack: Stack, out: CodeBuffer) -> None:
        copy_var = stack.push()
        out.write(ASTSetInt([copy_var], 0))

        out.write(
            ASTWhile(self.right, [
                ASTIsubInt([self.right], 1),
                ASTIaddInt(self.names, 1),
                ASTIaddInt([copy_var], 1)
            ]))

        out.write(
            ASTWhile(copy_var, [
                ASTIsubInt([copy_var], 1),
                ASTIaddInt([self.right], 1)
            ]))

        stack.pop(copy_var)


class ASTIsubVar(IProcessable):
    def __init__(self, names: List[IGetter], right: IGetter):
        self.names: List[IGetter] = names
        self.right: IGetter = right

    def __str__(self):
        return f"{str(self.names)[1:-1]} -= {self.right}"

    def process(self, declarations: Dict[str, CodeVar], stack: Stack, out: CodeBuffer) -> None:
        copy_var = stack.push()
        out.write(ASTSetInt([copy_var], 0))

        out.write(
            ASTWhile(self.right, [
                ASTIsubInt([self.right], 1),
                ASTIsubInt(self.names, 1),
                ASTIaddInt([copy_var], 1)
            ]))

        out.write(
            ASTWhile(copy_var, [
                ASTIsubInt([copy_var], 1),
                ASTIaddInt([self.right], 1)
            ]))

        stack.pop(copy_var)


class ASTSetVar(IProcessable):
    def __init__(self, names: List[IGetter], right: IGetter):
        self.names: List[IGetter] = names
        self.right: IGetter = right

    def __str__(self):
        return f"{str(self.names)[1:-1]} = {self.right}"

    def process(self, declarations: Dict[str, CodeVar], stack: Stack, out: CodeBuffer) -> None:
        out.write(ASTSetInt(self.names, 0))

        copy_var = stack.push()
        out.write(ASTSetInt([copy_var], 0))
        out.write(Goto(self.right))
        out.write("[-")
        for i in self.names:
            out.write(Goto(i))
            out.write("+")
        out.write(Goto(copy_var))
        out.write("+")
        out.write(Goto(self.right))
        out.write("]")

        out.write(Goto(copy_var))
        out.write("[-")
        out.write(Goto(self.right))
        out.write("+")
        out.write(Goto(copy_var))
        out.write("]")

        stack.pop(copy_var)


class ASTIf(IProcessable):
    def __init__(self, test_var: IGetter, code: List[IProcessable]):
        self.test_var: IGetter = test_var
        self.code: List[IProcessable] = code

    def __str__(self):
        return f"if({self.test_var})"

    def process(self, declarations: Dict[str, CodeVar], stack: Stack, out: CodeBuffer) -> None:
        copy_var = stack.push()
        out.write(ASTSetVar([copy_var], self.test_var))
        out.write(ASTWhile(copy_var, self.code + [ASTSetInt([copy_var], 0)]))
        stack.pop(copy_var)


class ASTIfElif(IProcessable):
    def __init__(self, data: List[Tuple[IGetter, List[IProcessable]]], code_else: List[IProcessable] = None):
        self.data: List[Tuple[IGetter, List[IProcessable]]] = data
        self.code_else: List[IProcessable] = code_else

    def __str__(self):
        return f"if({self.data[0][0]})" + \
               "".join(f"elif({i[0]})" for i in self.data) + \
               f"else" if self.code_else is not None else ""

    def process(self, declarations: Dict[str, CodeVar], stack: Stack, out: CodeBuffer) -> None:
        else_flag = stack.push()
        out.write(ASTSetInt([else_flag], 1))
        out.write(ASTIf(self.data[0][0], self.data[0][1] + [ASTSetInt([else_flag], 0)]))
        for i in self.data[1:]:
            out.write(ASTIf(
                else_flag,
                [ASTIf(i[0], i[1] + [ASTSetInt([else_flag], 0)])]
            ))
        if self.code_else is not None:
            out.write(ASTIf(else_flag, self.code_else))
        stack.pop(else_flag)


class ASTCase(IProcessable):
    def __init__(self, test_var: IGetter, code: List[Tuple[int, List[IProcessable]]]):
        self.test_var: IGetter = test_var
        self.code: List[Tuple[int, List[IProcessable]]] = code

    def process(self, declarations: Dict[str, CodeVar], stack: Stack, out: CodeBuffer) -> None:
        if len(self.code) != 0:
            copy_var = stack.push()
            out.write(ASTSetVar([copy_var], self.test_var))
            last = 0
            for i in self.code:
                out.write(ASTIsubInt([copy_var], i[0] - last))
                out.write(ASTIfElif([(copy_var, [])], code_else=i[1]))
                last = i[0]

            stack.pop(copy_var)


class ASTIdivVar(IProcessable):
    def __init__(self, names: List[IGetter], right: IGetter):
        self.names: List[IGetter] = names
        self.right: IGetter = right

    def process(self, declarations: Dict[str, CodeVar], stack: Stack, out: CodeBuffer) -> None:
        for left in self.names:
            work = stack.push()
            out.write(ASTSetInt([work], 1))
            counter = stack.push()
            out.write(ASTSetInt([counter], 0))
            left_var = stack.push()
            out.write(ASTSetVar([left_var], left))
            right_var = stack.push()

            out.write(ASTWhile(work, [
                ASTSetVar([right_var], self.right),
                ASTWhile(right_var, [
                    ASTIfElif([(left_var, [])], code_else=[
                        ASTSetInt([work], 0),
                        ASTSetInt([left_var, right_var], 1),
                    ]),
                    ASTIsubInt([left_var, right_var], 1),
                ]),
                ASTIaddInt([counter], 1),
            ]))
            out.write(ASTIsubInt([counter], 1))
            out.write(ASTSetVar([left], counter))
            stack.pop(right_var)
            stack.pop(left_var)
            stack.pop(counter)
            stack.pop(work)


class ASTImodVar(IProcessable):
    def __init__(self, names: List[IGetter], right: IGetter):
        self.names: List[IGetter] = names
        self.right: IGetter = right

    def process(self, declarations: Dict[str, CodeVar], stack: Stack, out: CodeBuffer) -> None:
        for left in self.names:
            work = stack.push()
            out.write(ASTSetInt([work], 1))
            left_var = stack.push()
            out.write(ASTSetVar([left_var], left))
            right_var = stack.push()

            out.write(ASTWhile(work, [
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
            ]))
            stack.pop(right_var)
            stack.pop(left_var)
            stack.pop(work)


class ASTIdivInt(IProcessable):
    def __init__(self, names: List[IGetter], num: int):
        self.names: List[IGetter] = names
        self.num: int = num

    def process(self, declarations: Dict[str, CodeVar], stack: Stack, out: CodeBuffer) -> None:
        for left in self.names:
            if self.num == 0:
                out.write(ASTSetInt([left], -1))
                continue
            work = stack.push()
            out.write(ASTSetInt([work], 1))
            counter = stack.push()
            out.write(ASTSetInt([counter], 0))
            left_var = stack.push()
            out.write(ASTSetVar([left_var], left))
            right_var = stack.push()

            out.write(ASTWhile(work, [
                ASTSetInt([right_var], self.num),
                ASTWhile(right_var, [
                    ASTIfElif([(left_var, [])], code_else=[
                        ASTSetInt([work], 0),
                        ASTSetInt([left_var, right_var], 1),
                    ]),
                    ASTIsubInt([left_var, right_var], 1),
                ]),
                ASTIaddInt([counter], 1),
            ]))
            out.write(ASTIsubInt([counter], 1))
            out.write(ASTSetVar([left], counter))
            stack.pop(right_var)
            stack.pop(left_var)
            stack.pop(counter)
            stack.pop(work)


class ASTImodInt(IProcessable):
    def __init__(self, names: List[IGetter], num: int):
        self.names: List[IGetter] = names
        self.num: int = num

    def process(self, declarations: Dict[str, CodeVar], stack: Stack, out: CodeBuffer) -> None:
        for left in self.names:
            if self.num == 0:
                out.write(ASTSetInt([left], -1))
                continue

            work = stack.push()
            out.write(ASTSetInt([work], 1))
            left_var = stack.push()
            out.write(ASTSetVar([left_var], left))
            right_var = stack.push()

            out.write(ASTWhile(work, [
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
            ]))
            stack.pop(right_var)
            stack.pop(left_var)
            stack.pop(work)


class ASTImulVar(IProcessable):
    def __init__(self, names: List[IGetter], right: IGetter):
        self.names: List[IGetter] = names
        self.right: IGetter = right

    def process(self, declarations: Dict[str, CodeVar], stack: Stack, out: CodeBuffer) -> None:
        for left in self.names:
            copy_var = stack.push()
            copy_var2 = stack.push()
            out.write(ASTSetVar([copy_var], left))
            out.write(ASTSetVar([copy_var2], self.right))
            out.write(ASTSetInt([left], 0))
            out.write(ASTWhile(copy_var2, [
                ASTIsubInt([copy_var2], 1),
                ASTIaddVar([left], copy_var),
            ]))
            stack.pop(copy_var2)
            stack.pop(copy_var)


class ASTImulInt(IProcessable):
    def __init__(self, names: List[IGetter], num: int):
        self.names: List[IGetter] = names
        self.num: int = num

    def process(self, declarations: Dict[str, CodeVar], stack: Stack, out: CodeBuffer) -> None:
        if self.num == 0:
            out.write(ASTSetInt(self.names, 0))
            return

        if abs(self.num) >= 16:
            copy_var = stack.push()
            out.write(ASTSetInt([copy_var], self.num))
            out.write(ASTImulVar(self.names, copy_var))
            stack.pop(copy_var)
            return

        for left in self.names:
            copy_var = stack.push()
            out.write(ASTSetVar([copy_var], left))
            for _ in range(self.num - 1):
                out.write(ASTIaddVar([left], copy_var))
            stack.pop(copy_var)


class ASTIlshiftInt(IProcessable):
    def __init__(self, names: List[IGetter], num: int):
        self.names: List[IGetter] = names
        self.num: int = num

    def process(self, declarations: Dict[str, CodeVar], stack: Stack, out: CodeBuffer) -> None:
        if self.num == 0:
            return
        out.write(ASTImulInt(self.names, 2 ** self.num))


class ASTIrshiftInt(IProcessable):
    def __init__(self, names: List[IGetter], num: int):
        self.names: List[IGetter] = names
        self.num: int = num

    def process(self, declarations: Dict[str, CodeVar], stack: Stack, out: CodeBuffer) -> None:
        if self.num == 0:
            return
        out.write(ASTIdivInt(self.names, 2 ** self.num))


class ASTIlshiftVar(IProcessable):
    def __init__(self, names: List[IGetter], right: IGetter):
        self.names: List[IGetter] = names
        self.right: IGetter = right

    def process(self, declarations: Dict[str, CodeVar], stack: Stack, out: CodeBuffer) -> None:
        copy_var = stack.push()
        out.write(ASTSetVar([copy_var], self.right))
        out.write(ASTWhile(copy_var, [
            ASTIsubInt([copy_var], 1),
            ASTIlshiftInt(self.names, 1),
        ]))
        stack.pop(copy_var)


class ASTIrshiftVar(IProcessable):
    def __init__(self, names: List[IGetter], right: IGetter):
        self.names: List[IGetter] = names
        self.right: IGetter = right

    def process(self, declarations: Dict[str, CodeVar], stack: Stack, out: CodeBuffer) -> None:
        copy_var = stack.push()
        out.write(ASTSetVar([copy_var], self.right))
        out.write(ASTWhile(copy_var, [
            ASTIsubInt([copy_var], 1),
            ASTIrshiftInt(self.names, 1),
        ]))
        stack.pop(copy_var)


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
