from collections import OrderedDict
from typing import Dict

from ply import yacc

from code_ast import ASTIntDeclaration, ASTFile, ASTAssembler, ASTGoto, ASTOut, ASTIn, ASTSetInt, ASTSetVar, ASTIaddInt, \
    ASTIsubInt, ASTIaddVar, ASTIsubVar, ASTWhile, ASTIf, ASTIfElif, IDeclaration, ASTStringDeclaration


class CodeParser:
    def __init__(self, tokens, literals, **kwargs):
        self.vars_declarations: Dict[str, IDeclaration] = OrderedDict({
            "False": ASTIntDeclaration("False", 0),
            "True": ASTIntDeclaration("True", 1),
            "__copy_var": ASTIntDeclaration("__copy_var", 0),
            "__else_flag": ASTIntDeclaration("__else_flag", 0),
        })

        self.tokens = tokens
        self.literals = literals
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
            p[0].declarations = self.vars_declarations
        elif len(p) == 3:
            p[0] = p[1]
            if isinstance(p[2], IDeclaration):
                if p[2] in self.vars_declarations.keys():
                    raise Exception(f"[:?]Redeclaration ID {p[2]}")

                self.vars_declarations[p[2].name] = p[2]
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

    def p_declaration_int(self, p):
        """declaration  : int ID '=' expr ';'
                        | int ID ';'"""
        if len(p) == 4:
            p[0] = ASTIntDeclaration(p[2], 0)
            return
        p[0] = ASTIntDeclaration(p[2], p[4])

    def p_declaration_string(self, p):
        """declaration  : string ID '=' STRING ';'"""
        p[0] = ASTStringDeclaration(p[2], p[4])

    def p_code_asm(self, p):
        """code : asm '(' STRING ')' ';'"""
        if not all(i in "+-[]<>.," for i in p[3]):
            raise Exception(f"[:{p.slice[1].lineno}]Incorrect symbol in asm line")
        p[0] = ASTAssembler(p[3])

    def p_code_goto(self, p):
        """code  : goto id ';'"""
        p[0] = ASTGoto(p[2])

    def p_code_in(self, p):
        """code  : in id ';'"""
        p[0] = ASTIn(p[2])

    def p_code_out(self, p):
        """code  : out id ';'"""
        p[0] = ASTOut(p[2])

    def p_left_operands_start(self, p):
        """left_operands     : id"""
        p[0] = [p[1]]

    def p_left_operands_id(self, p):
        """left_operands    : left_operands ',' id"""
        p[0] = p[1]
        p[0].append(p[3])

    def p_code_set_int(self, p):
        """code     : left_operands '=' expr ';'
                    | left_operands IADD expr ';'
                    | left_operands ISUB expr ';'"""
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
        """code     : left_operands '=' id ';'
                    | left_operands IADD id ';'
                    | left_operands ISUB id ';'"""
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
        """code : while '(' id ')' block_code"""
        p[0] = ASTWhile(p[3], p[5])

    def p_astif(self, p):
        """astif : if '(' id ')' block_code"""
        p[0] = ASTIf(p[3], p[5])

    def p_astif_elif_if(self, p):
        """astif_elif : astif elif '(' id ')' block_code"""
        p[0] = ASTIfElif([(p[1].test_var, p[1].code), (p[4], p[6])])

    def p_astif_elif_elif(self, p):
        """astif_elif : astif_elif elif '(' id ')' block_code"""
        p[0] = p[1]
        p[0].data.append((p[4], p[6]))

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

    def p_id_id(self, p):
        """id   : ID"""
        if p[1] not in self.vars_declarations.keys():
            raise Exception(f"[:{p.slice[1].lineno}]Unknown ID {p[1]}")
        p[0] = p[1]

    def p_id_index(self, p):
        """id   : id '[' INTEGER ']'"""
        p[0] = f"{p[1]}[{p[3]}]"

