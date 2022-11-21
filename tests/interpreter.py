from threading import Thread
from typing import Dict, List, Iterable, Iterator


class InterpreterState:
    def __init__(self, mem_len: int = 1000):
        self.mem: bytearray = bytearray(mem_len)
        self.cursor_pos: int = 0

    @property
    def cursor(self) -> int:
        return (self.mem[self.cursor_pos] % 256 + 256) % 256

    @cursor.setter
    def cursor(self, var: int):
        self.mem[self.cursor_pos] = (var % 256 + 256) % 256


class IInterInst:
    def process(self, state: InterpreterState):
        raise Exception

    def get_size(self) -> int:
        raise Exception


class CurMove(IInterInst):
    def __init__(self, shift: int):
        self.shift: int = shift

    def __repr__(self):
        return f"CurMove({self.shift})"

    def process(self, state: InterpreterState):
        state.cursor_pos += self.shift

    def get_size(self) -> int:
        return abs(self.shift)


class CurAdd(IInterInst):
    def __init__(self, var: int):
        self.var: int = var

    def __repr__(self):
        return f"CurAdd({self.var})"

    def process(self, state: InterpreterState):
        state.cursor += self.var

    def get_size(self) -> int:
        return abs(self.var)


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
        start_end: Dict[int, int] = {}
        end_start: Dict[int, int] = {}
        stack: List[int] = []

        for i, f in enumerate(self.proc_code):
            if f == "[":
                stack.append(i)
            if f == "]":
                start_end[stack.pop()] = i
        assert len(stack) == 0, "not enough right brackets"

        for i, f in start_end.items():
            end_start[f] = i

        state: InterpreterState = InterpreterState()
        pos = 0
        counter = 0

        last_counter = 0

        while pos < len(self.proc_code):
            if self.stopped:
                break

            if last_counter // 1000000 < counter // 1000000:
                print(counter)

            last_counter = counter

            match self.proc_code[pos]:
                case IInterInst() as inst:
                    inst.process(state)
                    counter += inst.get_size() - 1
                    pos += 1
                case ".":
                    self.out.append(state.cursor)
                    pos += 1
                case ",":
                    state.cursor = next(self.inp)
                    pos += 1
                case "[":
                    if state.cursor == 0:
                        pos = start_end[pos] + 1
                    else:
                        pos += 1
                case "]":
                    if state.cursor != 0:
                        pos = end_start[pos] + 1
                    else:
                        pos += 1
                case "0":
                    state.cursor = 0
                    pos += 1
                case _:
                    pos += 1
        pass

    def generate_proc_code(self):
        self.proc_code = []
        last = None
        for i in self.code.replace("[-]", "0"):
            match i:
                case "." | "," | "[" | "]":
                    last = i
                    self.proc_code.append(i)
                case "0":
                    last = i
                    self.proc_code.append(i)
                case ">" | "<":
                    if not isinstance(last, CurMove):
                        last = CurMove(0)
                        self.proc_code.append(last)
                    last.shift += 1 if i == ">" else -1
                case "+" | "-":
                    if not isinstance(last, CurAdd):
                        last = CurAdd(0)
                        self.proc_code.append(last)
                    last.var += 1 if i == "+" else -1

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
