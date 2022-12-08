from .lexer import *
from .linker import *
from .parser import *
from .preprocessor import Preprocessor


def compile_code(data: str, definitions: Dict[str, str] = None) -> str:
    if definitions is None:
        definitions = {}
    definitions_2: Dict[str, List] = {}
    for i, f in definitions.items():
        lexer_ = CodeLexer()
        lexer_.lexer.input(f)
        definitions_2[i] = list(lexer_.lexer)

    code_parser = CodeParser(CodeLexer.tokens, CodeLexer.literals)

    a: ASTFile = (code_parser.parse(input=data + "\n", lexer=Preprocessor(declarations=definitions_2)))

    if not code_parser.parser.errorok:
        raise Exception

    return CodeLinker(a).process()
