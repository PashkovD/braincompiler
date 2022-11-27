from threading import Thread
from typing import Dict, List, Iterable, Iterator, Union


class InterpreterState:
    def __init__(self, inp: Iterator[int], out: bytearray, mem_len: int = 1000):
        self.inp: Iterator[int] = inp
        self.out: bytearray = out
        self.mem: bytearray = bytearray(mem_len)
        self.cursor_pos: int = 0

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
        self.stopped: bool = False
        self.proc_code: list = []

    def run(self) -> None:
        # start_end: Dict[int, int] = {}
        # end_start: Dict[int, int] = {}
        # stack: List[int] = []
        #
        # for i, f in enumerate(self.proc_code):
        #     if f == "[":
        #         stack.append(i)
        #     if f == "]":
        #         start_end[stack.pop()] = i
        # assert len(stack) == 0, "not enough right brackets"
        #
        # for i, f in start_end.items():
        #     end_start[f] = i

        state: InterpreterState = InterpreterState(self.inp, self.out)
        pos = 0

        while pos < len(self.proc_code):
            if self.stopped:
                break

            match self.proc_code[pos]:
                case IInterInst() as inst:
                    inst.process(state)
                    pos += 1
                # case "[":
                #     if state.cursor == 0:
                #         pos = start_end[pos] + 1
                #     else:
                #         pos += 1
                # case "]":
                #     if state.cursor != 0:
                #         pos = end_start[pos] + 1
                #     else:
                #         pos += 1
                case _:
                    pos += 1
        pass

    def generate_proc_code(self):
        self.proc_code = []
        CodeBlock.parse("", iter(self.code.replace("[-]", "0")), self.proc_code)
        pass
        # last = None
        # for i in self.code.replace("[-]", "0"):
        #     match i:
        #         case "[" | "]":
        #             last = i
        #             self.proc_code.append(last)
        #         case ".":
        #             last = CurOut()
        #             self.proc_code.append(last)
        #         case ",":
        #             last = CurIn()
        #             self.proc_code.append(last)
        #         case "0":
        #             last = CurSet(0)
        #             self.proc_code.append(last)
        #         case ">" | "<":
        #             if not isinstance(last, CurMove):
        #                 last = CurMove(0)
        #                 self.proc_code.append(last)
        #             last.shift += 1 if i == ">" else -1
        #         case "+" | "-":
        #             if not isinstance(last, CurAdd):
        #                 last = CurAdd(0)
        #                 self.proc_code.append(last)
        #             last.var += 1 if i == "+" else -1

    def __call__(self, code: str, inp: Iterable[int]):
        self.code = code
        self.inp = iter(inp)
        self.out = bytearray()
        self.stopped = False
        self.generate_proc_code()

        self.start()
        self.join(self.timeout)
        if self.is_alive():
            self.stopped = True
            raise TimeoutError
        return self.out
