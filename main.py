from code_ast import ASTFile
from lexer import CodeLexer
from linker import CodeLinker
from parser import CodeParser


def main():
    with open("example/code2.txt") as f:
        a: ASTFile = (CodeParser(CodeLexer.tokens).parse(input=f.read() + "\n", lexer=CodeLexer().lexer))

    if not isinstance(a, ASTFile):
        raise Exception

    data = CodeLinker(a).process()
    for i in range(0, len(data), 100):
        print(data[i:i+100])


if __name__ == '__main__':
    main()
