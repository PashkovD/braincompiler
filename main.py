from code_ast import ASTFile
from lexer import CodeLexer
from linker import CodeLinker
from parser import CodeParser


def main():
    lexer = CodeLexer()
    parser = CodeParser(lexer.tokens, lexer.literals)
    with open("example/code.txt") as f:
        a: ASTFile = (parser.parse(input=f.read() + "\n", lexer=lexer.lexer))

    if not parser.parser.errorok:
        raise Exception

    data = CodeLinker(a).process()
    for i in range(0, len(data), 100):
        print(data[i:i+100])


if __name__ == '__main__':
    main()
