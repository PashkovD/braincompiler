from threading import Thread
from typing import Dict, List, Iterable, Iterator, Union

class InterStop(Exception):
    ...

class InterpreterState:
    def __init__(self, inp: Iterator[int], out: bytearray, mem_len: int = 1000):
        self.inp: Iterator[int] = inp
        self.out: bytearray = out
        self.mem: bytearray = bytearray(mem_len)
        self.cursor_pos: int = 0
        self.stopped = False

    @property
    def cursor(self) -> int:
        return (self.mem[self.cursor_pos] % 256 + 256) % 256

    @cursor.setter
    def cursor(self, var: int):
        self.mem[self.cursor_pos] = (var % 256 + 256) % 256


class IInterInst:

    @classmethod
    def parse(cls, current: str, code: Iterator[str], out: List[Union[str, "IInterInst"]]):
        raise Exception

    def process(self, state: InterpreterState):
        raise Exception


parsing_dict: Dict[str, IInterInst] = {}


class CodeBlock(IInterInst):
    def __init__(self, code: List[IInterInst]):
        self.code: List[IInterInst] = code

    @classmethod
    def parse(cls, current: str, code: Iterator[str], out: List[Union[str, IInterInst]]):
        data = []
        while True:
            var = next(code, None)
            if var is None:
                break
            if var in parsing_dict.keys():
                parsing_dict[var].parse(var, code, data)
        out.append(CodeBlock(data))

    def process(self, state: InterpreterState):
        for i in self.code:
            if state.stopped:
                raise InterStop
            i.process(state)


class CurMove(IInterInst):
    def __init__(self, shift: int):
        self.shift: int = shift

    def __repr__(self):
        return f"CurMove({self.shift})"

    @classmethod
    def parse(cls, current: str, code: Iterator[str], out: List[Union[str, IInterInst, "CurMove"]]):
        if not (len(out) >= 1 and isinstance(out[-1], CurMove)):
            out.append(CurMove(0))

        out[-1].shift += 1 if current == ">" else -1

    def process(self, state: InterpreterState):
        state.cursor_pos += self.shift


parsing_dict |= {">": CurMove, "<": CurMove}


class CurAdd(IInterInst):
    def __init__(self, var: int):
        self.var: int = var

    def __repr__(self):
        return f"CurAdd({self.var})"

    @classmethod
    def parse(cls, current: str, code: Iterator[str], out: List[Union[str, IInterInst, "CurAdd"]]):
        if not (len(out) >= 1 and isinstance(out[-1], CurAdd)):
            out.append(CurAdd(0))

        out[-1].var += 1 if current == "+" else -1

    def process(self, state: InterpreterState):
        state.cursor += self.var


parsing_dict |= {"+": CurAdd, "-": CurAdd}


class CurSet(CurAdd):
    def __repr__(self):
        return f"CurSet({self.var})"

    @classmethod
    def parse(cls, current: str, code: Iterator[str], out: List[Union[str, IInterInst, "CurAdd"]]):
        if current == "0":
            out.append(CurSet(0))
            return
        super().parse(current, code, out)

    def process(self, state: InterpreterState):
        state.cursor = self.var


parsing_dict |= {"0": CurSet}


class CurIn(IInterInst):
    @classmethod
    def parse(cls, current: str, code: Iterator[str], out: List[Union[str, IInterInst]]):
        out.append(cls())

    def process(self, state: InterpreterState):
        state.cursor = next(state.inp)


parsing_dict |= {",": CurIn}


class CurOut(IInterInst):
    @classmethod
    def parse(cls, current: str, code: Iterator[str], out: List[Union[str, IInterInst]]):
        out.append(cls())

    def process(self, state: InterpreterState):
        state.out.append(state.cursor)


parsing_dict |= {".": CurOut}


class InterMoveVar(IInterInst):
    def __init__(self, data: Dict[int, int]):
        self.data: Dict[int, int] = data

    @classmethod
    def is_move_var(cls, code: List[IInterInst]) -> bool:
        zero_add = 0
        pos = 0
        for i in code:
            if type(i) not in (CurAdd, CurMove):
                return False
            if isinstance(i, CurMove):
                pos += i.shift
            if pos == 0 and isinstance(i, CurAdd):
                zero_add += i.var
        return pos == 0 and zero_add == -1

    @classmethod
    def generate(cls, code: List[Union[CurAdd, CurMove]]) -> "InterMoveVar":
        data: Dict[int, int] = {}
        pos = 0
        for i in code:
            if isinstance(i, CurAdd):
                data[pos] = data.get(pos, 0) + i.var
            if isinstance(i, CurMove):
                pos += i.shift
        return InterMoveVar(data)

    def process(self, state: InterpreterState):
        var = state.cursor
        zero_pos = state.cursor_pos
        for i, f in self.data.items():
            state.cursor_pos = zero_pos + i
            state.cursor += var * f
        state.cursor_pos = zero_pos


class InterWhile(CodeBlock):
    @classmethod
    def parse(cls, current: str, code: Iterator[str], out: List[Union[str, IInterInst]]):
        data = []
        while True:
            var = next(code)
            if var == "]":
                break
            if var in parsing_dict.keys():
                parsing_dict[var].parse(var, code, data)
        if InterMoveVar.is_move_var(data):
            out.append(InterMoveVar.generate(data))
            return
        out.append(InterWhile(data))

    def process(self, state: InterpreterState):
        while state.cursor != 0:
            super().process(state)


parsing_dict |= {"[": InterWhile}


class Interpreter(Thread):
    def __init__(self, timeout: int = 0.1):
        super().__init__()
        self.timeout: int = timeout
        self.inp: Iterator[int] = []
        self.out: bytearray = bytearray()
        self.code: str = ""
        self.proc_code: List[CodeBlock] = []
        self.state = None

    def run(self) -> None:
        self.state: InterpreterState = InterpreterState(self.inp, self.out)
        try:
            self.proc_code[-1].process(self.state)
        except InterStop:
            pass
        print("stop", self.name)

    def generate_proc_code(self):
        self.proc_code = []
        CodeBlock.parse("", iter(self.code.replace("[-]", "0")), self.proc_code)

    def __call__(self, code: str, inp: Iterable[int]):
        self.code = code
        self.inp = iter(inp)
        self.out = bytearray()
        self.generate_proc_code()

        self.start()
        self.join(self.timeout)
        if self.is_alive():
            self.state.stopped = True
            raise TimeoutError
        self.state.stopped = True
        return self.out
