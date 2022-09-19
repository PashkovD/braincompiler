from lexer import CodeLexer
from parser import CodeParser


def main():
    with open("example/code2.txt") as f:
        a = (CodeParser(CodeLexer.tokens).parse(input=f.read(), lexer=CodeLexer().lexer))
    pass


if __name__ == '__main__':
    main()
