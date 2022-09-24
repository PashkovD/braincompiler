from collections import OrderedDict
from typing import Dict

from ply import yacc

from code_ast import ASTDeclaration, ASTFile, ASTAssembler, ASTGoto, ASTOut, ASTIn, ASTSetInt, ASTSetVar, ASTIaddInt, \
    ASTIsubInt, ASTIaddVar, ASTIsubVar, ASTWhile, ASTIf, ASTIfElif


class CodeParser:
    def __init__(self, tokens, **kwargs):
        self.declarations: Dict[str, ASTDeclaration] = OrderedDict({
            "False": ASTDeclaration("False", 0),
            "True": ASTDeclaration("True", 1),
            "__copy_var": ASTDeclaration("__copy_var", 0),
            "__else_flag": ASTDeclaration("__else_flag", 0),
        })
        self.tokens = tokens
        self.parser = yacc.yacc(module=self, **kwargs)

    def parse(self, **kwargs):
        return self.parser.parse(**kwargs)

    start = "file"

    def p_error(self, p):
        pass

    def p_file(self, p):
        """file :
                | file declaration
                | file assembler
                | file astgoto
                | file astout
                | file astin
                | file astset
                | file astwhile
                | file astif
                | file astif_elif"""
        if len(p) == 1:
            p[0] = ASTFile()
            p[0].declarations = self.declarations
        elif len(p) == 3:
            p[0] = p[1]
            if isinstance(p[2], ASTDeclaration):
                if p[2] in self.declarations.keys():
                    raise Exception(f"[:?]Redeclaration ID {p[2]}")

                self.declarations[p[2].name] = p[2]
                return
            p[0].code.append(p[2])

    def p_code_block_start(self, p):
        """code_block   : '{' """
        p[0] = []

    def p_code_block_code(self, p):
        """code_block   : code_block assembler
                        | code_block astgoto
                        | code_block astout
                        | code_block astin
                        | code_block astset
                        | code_block astwhile
                        | code_block astif
                        | code_block astif_elif"""
        p[0] = p[1]
        p[0].append(p[2])

    def p_declaration(self, p):
        """declaration  : int ID '=' INTEGER ';'
                        | int ID '=' STRING ';'
                        | int ID ';'"""
        if len(p) == 4:
            p[0] = ASTDeclaration(p[2], 0)
            return
        if isinstance(p[4], str):
            p[4] = ord(p[4])
        p[0] = ASTDeclaration(p[2], p[4])

    def p_assembler(self, p):
        """assembler  : asm '(' STRING ')' ';'"""
        if not all(i in "+-[]<>.," for i in p[3]):
            raise Exception(f"[:{p.slice[1].lineno}]Incorrect symbol in asm line")
        p[0] = ASTAssembler(p[3])

    def p_astgoto(self, p):
        """astgoto  : goto ID ';'"""
        if p[2] not in self.declarations.keys():
            raise Exception(f"[:{p.slice[1].lineno}]Unknown ID {p[2]}")
        p[0] = ASTGoto(p[2])

    def p_astin(self, p):
        """astin  : in ID ';'"""
        if p[2] not in self.declarations.keys():
            raise Exception(f"[:{p.slice[1].lineno}]Unknown ID {p[2]}")
        p[0] = ASTIn(p[2])

    def p_astout(self, p):
        """astout  : out ID ';'"""
        if p[2] not in self.declarations.keys():
            raise Exception(f"[:{p.slice[1].lineno}]Unknown ID {p[2]}")
        p[0] = ASTOut(p[2])

    def p_left_operands_start(self, p):
        """left_operands     : ID"""
        if p[1] not in self.declarations.keys():
            raise Exception(f"[:{p.slice[1].lineno}]Unknown ID {p[1]}")
        p[0] = [p[1]]

    def p_left_operands_id(self, p):
        """left_operands    : left_operands ',' ID"""
        if p[3] not in self.declarations.keys():
            raise Exception(f"[:{p.slice[1].lineno}]Unknown ID {p[3]}")
        p[0] = p[1]
        p[0].append(p[3])

    def p_astset_int(self, p):
        """astset   : left_operands '=' INTEGER ';'
                    | left_operands IADD INTEGER ';'
                    | left_operands ISUB INTEGER ';'
                    | left_operands '=' STRING ';'
                    | left_operands IADD STRING ';'
                    | left_operands ISUB STRING ';'"""
        decs = self.declarations.keys()
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
        """astset   : left_operands '=' ID ';'
                    | left_operands IADD ID ';'
                    | left_operands ISUB ID ';'"""
        decs = self.declarations.keys()
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

    def p_astwhile(self, p):
        """astwhile : while '(' ID ')' code_block '}'"""
        if p[3] not in self.declarations.keys():
            raise Exception(f"[:{p.slice[1].lineno}]Unknown ID {p[3]}")

        p[0] = ASTWhile(p[3], p[5])

    def p_astif(self, p):
        """astif : if '(' ID ')' code_block '}'"""
        if p[3] not in self.declarations.keys():
            raise Exception(f"[:{p.slice[1].lineno}]Unknown ID {p[3]}")

        p[0] = ASTIf(p[3], p[5])

    def p_astif_elif_if(self, p):
        """astif_elif : astif elif '(' ID ')' code_block '}'"""
        if p[4] not in self.declarations.keys():
            raise Exception(f"[:{p.slice[1].lineno}]Unknown ID {p[4]}")

        p[0] = ASTIfElif([(p[1].test_var, p[1].code), (p[4], p[6])])

    def p_astif_elif_elif(self, p):
        """astif_elif : astif_elif elif '(' ID ')' code_block '}'"""
        if p[4] not in self.declarations.keys():
            raise Exception(f"[:{p.slice[1].lineno}]Unknown ID {p[4]}")
        p[0] = p[1]
        p[0].data.append((p[4], p[6].code))

    def p_astif_else_if(self, p):
        """astif_elif : astif else code_block '}'"""
        p[0] = ASTIfElif([(p[1].test_var, p[1].code)], p[3])

    def p_astif_else_elif(self, p):
        """astif_elif : astif_elif else code_block '}'"""
        p[0] = p[1]
        p[0].code_else = p[3]
