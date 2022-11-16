from threading import Thread
from typing import Dict, List, Iterable, Iterator


class Interpreter(Thread):
    def __init__(self, timeout: int = 0.1):
        super().__init__()
        self.timeout: int = timeout
        self.inp: Iterator[int] = []
        self.out: bytearray = bytearray()
        self.code: str = ""
        self.stopped: bool = False

    def run(self) -> None:
        start_end: Dict[int, int] = {}
        end_start: Dict[int, int] = {}
        stack: List[int] = []

        code = self.code.replace("[-]", "0")

        for i, f in enumerate(code):
            if f == "[":
                stack.append(i)
            if f == "]":
                start_end[stack.pop()] = i

        for i, f in start_end.items():
            end_start[f] = i

        mem: bytearray = bytearray(1000)
        cur = 0
        pos = 0
        while pos < len(code):
            if self.stopped:
                break

            match code[pos]:
                case "+":
                    mem[cur] = (mem[cur] + 1) % 256
                    pos += 1
                case "-":
                    mem[cur] = (mem[cur] + 255) % 256
                    pos += 1
                case "<":
                    cur -= 1
                    pos += 1
                case ">":
                    cur += 1
                    pos += 1
                case ".":
                    self.out.append(mem[cur])
                    pos += 1
                case ",":
                    mem[cur] = next(self.inp)
                    pos += 1
                case "[":
                    if mem[cur] == 0:
                        pos = start_end[pos] + 1
                    else:
                        pos += 1
                case "]":
                    if mem[cur] != 0:
                        pos = end_start[pos] + 1
                    else:
                        pos += 1
                case "0":
                    mem[cur] = 0
                    pos += 1
                case _:
                    pos += 1

    def __call__(self, code: str, inp: Iterable[int]):
        self.code = code
        self.inp = iter(inp)
        self.out = bytearray()
        self.stopped = False

        self.start()
        self.join(self.timeout)
        if self.is_alive():
            self.stopped = True
            raise TimeoutError
        return self.out
