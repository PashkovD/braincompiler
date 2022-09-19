def bf_add(num: int) -> str:
    if num > 0:
        return "+" * num
    if num == 0:
        return ""
    if num < 0:
        return "-" * -num


def bf_move(num: int) -> str:
    if num > 0:
        return ">" * num
    if num == 0:
        return ""
    if num < 0:
        return "<" * -num
