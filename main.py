from lexer import CodeLexer


def main():
    with open("example/code.txt") as f:
        CodeLexer().test(f.read())


if __name__ == '__main__':
    main()
