import sys
from argparse import ArgumentParser
from pathlib import PurePosixPath
from typing import List

from code_ast import ASTFile
from lexer import CodeLexer
from linker import CodeLinker
from parser import CodeParser


def compile_code(data: str) -> str:
    lexer = CodeLexer()
    parser = CodeParser(lexer.tokens, lexer.literals)

    a: ASTFile = (parser.parse(input=data + "\n", lexer=lexer.lexer))

    if not parser.parser.errorok:
        raise Exception

    return CodeLinker(a).process()


def main(args: List[str]):
    arg_parser = ArgumentParser(description="Compile simple language in brainfuck")
    arg_parser.add_argument('file', type=str, help='Input file')
    arg_parser.add_argument('-o', type=str, default=None, help='output file')
    names = arg_parser.parse_args(args[1:])

    with open(names.file) as f:
        data: str = compile_code(f.read())

    output = names.o
    if output is None:
        output = PurePosixPath(names.file).stem + ".bf"

    with open(output, "w") as f:
        for i in range(0, len(data), 100):
            f.write(data[i:i + 100] + "\n")


if __name__ == '__main__':
    main(sys.argv)
