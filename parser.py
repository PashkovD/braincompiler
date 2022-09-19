from typing import List

from ply import yacc

from code_ast import ASTDeclaration, ASTFile, ASTAssembler, ASTGoto


class CodeParser:
    def __init__(self, tokens, **kwargs):
        self.declarations: List[ASTDeclaration] = []
        self.tokens = tokens
        self.parser = yacc.yacc(module=self, **kwargs)

    def parse(self, **kwargs):
        return self.parser.parse(**kwargs)

    start = "file"

    def p_file(self, p):
        """file :
                | file declaration
                | file assembler
                | file astgoto"""
        if len(p) == 1:
            p[0] = ASTFile()
            p[0].declarations = self.declarations
        elif len(p) == 3:
            p[0] = p[1]
            if isinstance(p[2], ASTDeclaration):
                self.declarations.append(p[2])
                return
            p[0].code.append(p[2])

    def p_declaration(self, p):
        """declaration  : int ID '=' INTEGER NEWLINE
                        | int ID"""
        if len(p) == 3:
            p[0] = ASTDeclaration(p[2], 0)
            return
        p[0] = ASTDeclaration(p[2], p[4])

    def p_assembler(self, p):
        """assembler  : asm '(' STRING ')' NEWLINE"""
        if not all(i in "+-[]<>.,"for i in p[3]):
            raise Exception(f"[:{p.slice[1].lineno}]Incorrect symbol in asm line")
        p[0] = ASTAssembler(p[3])

    def p_astgoto(self, p):
        """astgoto  : goto ID NEWLINE"""
        if p[2] not in [i.name for i in self.declarations]:
            raise Exception(f"[:{p.slice[1].lineno}]Unknown ID {p[2]}")
        p[0] = ASTGoto(p[2])

