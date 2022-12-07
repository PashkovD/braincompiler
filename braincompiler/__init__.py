from .lexer import *
from .linker import *
from .parser import *
from .preprocessor import Preprocessor


def compile_code(data: str) -> str:
    code_parser = CodeParser(CodeLexer.tokens, CodeLexer.literals)

    a: ASTFile = (code_parser.parse(input=data + "\n", lexer=Preprocessor()))

    if not code_parser.parser.errorok:
        raise Exception

    return CodeLinker(a).process()
