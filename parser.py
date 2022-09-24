from collections import OrderedDict
from typing import Dict

from ply import yacc

from code_ast import ASTDeclaration, ASTFile, ASTAssembler, ASTGoto, ASTOut, ASTIn, ASTSetInt, ASTSetVar, ASTIaddInt, \
    ASTIsubInt, ASTIaddVar, ASTIsubVar, ASTWhile, ASTIf, ASTIfElif


class CodeParser:
    def __init__(self, tokens, literals, **kwargs):
        self.declarations: Dict[str, ASTDeclaration] = OrderedDict({
            "False": ASTDeclaration("False", 0),
            "True": ASTDeclaration("True", 1),
            "__copy_var": ASTDeclaration("__copy_var", 0),
            "__else_flag": ASTDeclaration("__else_flag", 0),
        })
        self.tokens = tokens
        self.parser = yacc.yacc(module=self, **kwargs)
        self.precedence = (
            ('left', '+', '-'),
            ('left', '*'),
        )

    def parse(self, **kwargs):
        return self.parser.parse(**kwargs)

    start = "file"

    def p_file(self, p):
        """file :
                | file declaration
                | file code"""
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

    def p_block_code_s_start(self, p):
        """block_code_s : '{' """
        p[0] = []

    def p_block_code_s_code(self, p):
        """block_code_s : block_code_s code"""
        p[0] = p[1]
        p[0].append(p[2])

    def p_block_code(self, p):
        """block_code   : block_code_s '}'"""
        p[0] = p[1]

    def p_declaration(self, p):
        """declaration  : int ID '=' expr ';'
                        | int ID ';'"""
        if len(p) == 4:
            p[0] = ASTDeclaration(p[2], 0)
            return
        if isinstance(p[4], str):
            p[4] = ord(p[4])
        p[0] = ASTDeclaration(p[2], p[4])

    def p_code_asm(self, p):
        """code : asm '(' STRING ')' ';'"""
        if not all(i in "+-[]<>.," for i in p[3]):
            raise Exception(f"[:{p.slice[1].lineno}]Incorrect symbol in asm line")
        p[0] = ASTAssembler(p[3])

    def p_code_goto(self, p):
        """code  : goto ID ';'"""
        if p[2] not in self.declarations.keys():
            raise Exception(f"[:{p.slice[1].lineno}]Unknown ID {p[2]}")
        p[0] = ASTGoto(p[2])

    def p_code_in(self, p):
        """code  : in ID ';'"""
        if p[2] not in self.declarations.keys():
            raise Exception(f"[:{p.slice[1].lineno}]Unknown ID {p[2]}")
        p[0] = ASTIn(p[2])

    def p_code_out(self, p):
        """code  : out ID ';'"""
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

    def p_code_set_int(self, p):
        """code     : left_operands '=' expr ';'
                    | left_operands IADD expr ';'
                    | left_operands ISUB expr ';'"""
        decs = self.declarations.keys()
        if not all(i in decs for i in p[1]):
            Exception(f"[:{p.slice[1].lineno}]Unknown ID in left operands")

        match p[2]:
            case "=":
                p[0] = ASTSetInt(p[1], p[3])
            case "+=":
                p[0] = ASTIaddInt(p[1], p[3])
            case "-=":
                p[0] = ASTIsubInt(p[1], p[3])
            case _ as e:
                raise Exception(e)

    def p_code_set_var(self, p):
        """code     : left_operands '=' ID ';'
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

    def p_code_while(self, p):
        """code : while '(' ID ')' block_code"""
        if p[3] not in self.declarations.keys():
            raise Exception(f"[:{p.slice[1].lineno}]Unknown ID {p[3]}")

        p[0] = ASTWhile(p[3], p[5])

    def p_astif(self, p):
        """astif : if '(' ID ')' block_code"""
        if p[3] not in self.declarations.keys():
            raise Exception(f"[:{p.slice[1].lineno}]Unknown ID {p[3]}")

        p[0] = ASTIf(p[3], p[5])

    def p_astif_elif_if(self, p):
        """astif_elif : astif elif '(' ID ')' block_code"""
        if p[4] not in self.declarations.keys():
            raise Exception(f"[:{p.slice[1].lineno}]Unknown ID {p[4]}")

        p[0] = ASTIfElif([(p[1].test_var, p[1].code), (p[4], p[6])])

    def p_astif_elif_elif(self, p):
        """astif_elif : astif_elif elif '(' ID ')' block_code"""
        if p[4] not in self.declarations.keys():
            raise Exception(f"[:{p.slice[1].lineno}]Unknown ID {p[4]}")
        p[0] = p[1]
        p[0].data.append((p[4], p[6].code))

    def p_astif_else_if(self, p):
        """astif_else : astif else block_code"""
        p[0] = ASTIfElif([(p[1].test_var, p[1].code)], p[3])

    def p_astif_else_elif(self, p):
        """astif_else : astif_elif else block_code"""
        p[0] = p[1]
        p[0].code_else = p[3]

    def p_code_if(self, p):
        """code : astif
                | astif_elif
                | astif_else"""
        p[0] = p[1]

    def p_expr_integer(self, p):
        """expr : INTEGER"""
        p[0] = p[1]

    def p_expr_string(self, p):
        """expr : STRING"""
        if len(p[1]) != 1:
            raise Exception(f"[:{p.slice[1].lineno}]Only allowed a string size of 1")
        p[0] = ord(p[1])

    def p_expr_binary(self, p):
        """expr : expr '+' expr
                | expr '-' expr
                | expr '*' expr"""
        if p[2] == '+':
            p[0] = p[1] + p[3]
        elif p[2] == '-':
            p[0] = p[1] - p[3]
        elif p[2] == '*':
            p[0] = p[1] * p[3]
        else:
            raise Exception

    def p_expr_brackets(self, p):
        """expr : '(' expr ')'"""
        p[0] = p[2]
