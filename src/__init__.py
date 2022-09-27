from .code_ast import *
from .goto import *
from .lexer import *
from .linker import *
from .parser import *
from .util import *


def compile_code(data: str) -> str:
    code_lexer = CodeLexer()
    code_parser = CodeParser(code_lexer.tokens, code_lexer.literals)

    a: ASTFile = (code_parser.parse(input=data + "\n", lexer=code_lexer.lexer))

    if not code_parser.parser.errorok:
        raise Exception

    return CodeLinker(a).process()
