from typing import List

from ply import yacc

from code_ast import ASTDeclaration, ASTFile, ASTAssembler, ASTGoto, ASTOut, ASTIn, ASTSetInt, ASTSetVar, ASTIaddInt, \
    ASTIsubInt, ASTIaddVar, ASTIsubVar, ASTWhile, ASTIf


class CodeParser:
    def __init__(self, tokens, **kwargs):
        self.declarations: List[ASTDeclaration] = [
            ASTDeclaration("False", 0),
            ASTDeclaration("True", 1),
            ASTDeclaration("__copy_var", 0),
        ]
        self.tokens = tokens
        self.parser = yacc.yacc(module=self, **kwargs)

    def parse(self, **kwargs):
        return self.parser.parse(**kwargs)

    start = "file"

    def p_file(self, p):
        """file :
                | file declaration
                | file assembler
                | file astgoto
                | file astout
                | file astin
                | file astset
                | file astwhile
                | file astif"""
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
                        | int ID '=' STRING NEWLINE
                        | int ID NEWLINE"""
        if len(p) == 4:
            p[0] = ASTDeclaration(p[2], 0)
            return
        if isinstance(p[4], str):
            p[4] = ord(p[4])
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

    def p_astin(self, p):
        """astin  : in ID NEWLINE"""
        if p[2] not in [i.name for i in self.declarations]:
            raise Exception(f"[:{p.slice[1].lineno}]Unknown ID {p[2]}")
        p[0] = ASTIn(p[2])

    def p_astout(self, p):
        """astout  : out ID NEWLINE"""
        if p[2] not in [i.name for i in self.declarations]:
            raise Exception(f"[:{p.slice[1].lineno}]Unknown ID {p[2]}")
        p[0] = ASTOut(p[2])

    def p_left_operands_start(self, p):
        """left_operands     : ID"""
        if p[1] not in [i.name for i in self.declarations]:
            raise Exception(f"[:{p.slice[1].lineno}]Unknown ID {p[1]}")
        p[0] = [p[1]]

    def p_left_operands_id(self, p):
        """left_operands    : left_operands ',' ID"""
        if p[3] not in [i.name for i in self.declarations]:
            raise Exception(f"[:{p.slice[1].lineno}]Unknown ID {p[3]}")
        p[0] = p[1]
        p[0].append(p[3])

    def p_astset_int(self, p):
        """astset   : left_operands '=' INTEGER NEWLINE
                    | left_operands IADD INTEGER NEWLINE
                    | left_operands ISUB INTEGER NEWLINE
                    | left_operands '=' STRING NEWLINE
                    | left_operands IADD STRING NEWLINE
                    | left_operands ISUB STRING NEWLINE"""
        decs = [i.name for i in self.declarations]
        if not all(i in decs for i in p[1]):
            Exception(f"[:{p.slice[1].lineno}]Unknown ID in left operands")

        if isinstance(p[3], str):
            p[3] = ord(p[3])

        match p[2]:
            case "=":
                p[0] = ASTSetInt(p[1], p[3])
            case "+=":
                p[0] = ASTIaddInt(p[1], p[3])
            case "-=":
                p[0] = ASTIsubInt(p[1], p[3])
            case _ as e:
                raise Exception(e)

    def p_astset_var(self, p):
        """astset   : left_operands '=' ID NEWLINE
                    | left_operands IADD ID NEWLINE
                    | left_operands ISUB ID NEWLINE"""
        decs = [i.name for i in self.declarations]
        if not all(i in decs for i in p[1]):
            Exception(f"[:{p.slice[1].lineno}]Unknown ID in left operands")
        if p[3] not in decs:
            Exception(f"[:{p.slice[1].lineno}]Unknown ID {p[3]}")
        match p[2]:
            case "=":
                p[0] = ASTSetVar(p[1], p[3])
            case "+=":
                p[0] = ASTIaddVar(p[1], p[3])
            case "-=":
                p[0] = ASTIsubVar(p[1], p[3])
            case _ as e:
                raise Exception(e)

    def p_code_block_start(self, p):
        """code_block   : '{' NEWLINE """
        p[0] = []

    def p_code_block_code(self, p):
        """code_block   : code_block assembler
                        | code_block astgoto
                        | code_block astout
                        | code_block astin
                        | code_block astset
                        | code_block astwhile
                        | code_block astif"""
        p[0] = p[1]
        p[0].append(p[2])

    def p_astwhile(self, p):
        """astwhile : while '(' ID ')' code_block '}' NEWLINE"""
        if p[3] not in [i.name for i in self.declarations]:
            raise Exception(f"[:{p.slice[1].lineno}]Unknown ID {p[3]}")

        p[0] = ASTWhile(p[3], p[5])

    def p_astif(self, p):
        """astif : if '(' ID ')' code_block '}' NEWLINE"""
        if p[3] not in [i.name for i in self.declarations]:
            raise Exception(f"[:{p.slice[1].lineno}]Unknown ID {p[3]}")

        p[0] = ASTIf(p[3], p[5])

