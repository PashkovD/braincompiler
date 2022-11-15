from typing import Dict, List, Iterable, Iterator


def process(code: str, inp: Iterable[int]) -> bytearray:
    start_end: Dict[int, int] = {}
    end_start: Dict[int, int] = {}
    stack: List[int] = []

    code = code.replace("[-]", "0")

    inp: Iterator[inp] = iter(inp)
    out: bytearray = bytearray()

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
                out.append(mem[cur])
                pos += 1
            case ",":
                mem[cur] = next(inp)
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
    return out
