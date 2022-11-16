from ply import yacc

from .ast_case import ASTCase
from .ast_iadd_int import ASTIaddInt
from .ast_iadd_var import ASTIaddVar
from .ast_idiv_int import ASTIdivInt
from .ast_idiv_var import ASTIdivVar
from .ast_if import ASTIf
from .ast_if_elif import ASTIfElif
from .ast_ilshift_int import ASTIlshiftInt
from .ast_ilshift_var import ASTIlshiftVar
from .ast_imod_int import ASTImodInt
from .ast_imod_var import ASTImodVar
from .ast_imul_int import ASTImulInt
from .ast_imul_var import ASTImulVar
from .ast_irshift_int import ASTIrshiftInt
from .ast_irshift_var import ASTIrshiftVar
from .ast_isub_int import ASTIsubInt
from .ast_isub_var import ASTIsubVar
from .ast_set_int import ASTSetInt
from .ast_set_var import ASTSetVar
from .base_ast import ASTAssembler, ASTGoto, ASTIn, ASTOut, ASTWhile
from .code_ast import *
from .code_getters import VarGetter, IndexGetter
from .declaration_ast import ASTIntDeclaration, ASTStringDeclaration


class CodeParser:
    def __init__(self, tokens, literals, **kwargs):
        self.vars_declarations: Dict[str, IDeclaration] = OrderedDict({})

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
        if not all(i in b"+-[]<>.,#" for i in p[3]):
            raise Exception(f"[:{p.slice[1].lineno}]Incorrect symbol in asm line")
        p[0] = ASTAssembler(p[3].decode("utf-8"))

    def p_code_asm_mul(self, p):
        """code : asm '(' STRING '*' expr ')' ';'"""
        if not all(i in b"+-[]<>.,#" for i in p[3]):
            raise Exception(f"[:{p.slice[1].lineno}]Incorrect symbol in asm line")
        p[0] = ASTAssembler(p[3].decode("utf-8") * p[5])

    def p_code_goto(self, p):
        """code  : goto id ';'"""
        p[0] = ASTGoto(p[2])

    def p_code_in(self, p):
        """code  : in id ';'"""
        p[0] = ASTIn(p[2])

    def p_code_out(self, p):
        """code  : out id ';'"""
        p[0] = ASTOut(p[2])

    def p_id_list_start(self, p):
        """id_list     : id"""
        p[0] = [p[1]]

    def p_id_list_id(self, p):
        """id_list    : id_list ',' id"""
        p[0] = p[1]
        p[0].append(p[3])

    def p_expr_list_start(self, p):
        """expr_list     : expr"""
        p[0] = [p[1]]

    def p_expr_list_id(self, p):
        """expr_list    : expr_list ',' expr"""
        p[0] = p[1]
        p[0].append(p[3])

    def p_code_set_int(self, p):
        """code     : id_list '=' expr ';'
                    | id_list IADD expr ';'
                    | id_list ISUB expr ';'
                    | id_list IDIV expr ';'
                    | id_list IMOD expr ';'
                    | id_list IMUL expr ';'
                    | id_list ILSHIFT expr ';'
                    | id_list IRSHIFT expr ';'"""
        match p[2]:
            case "=":
                p[0] = ASTSetInt(p[1], p[3])
            case "+=":
                p[0] = ASTIaddInt(p[1], p[3])
            case "-=":
                p[0] = ASTIsubInt(p[1], p[3])
            case "/=":
                p[0] = ASTIdivInt(p[1], p[3])
            case "%=":
                p[0] = ASTImodInt(p[1], p[3])
            case "*=":
                p[0] = ASTImulInt(p[1], p[3])
            case "<<=":
                p[0] = ASTIlshiftInt(p[1], p[3])
            case ">>=":
                p[0] = ASTIrshiftInt(p[1], p[3])
            case _ as e:
                raise Exception(e)

    def p_code_set_var(self, p):
        """code     : id_list '=' id ';'
                    | id_list IADD id ';'
                    | id_list ISUB id ';'
                    | id_list IDIV id ';'
                    | id_list IMOD id ';'
                    | id_list IMUL id ';'
                    | id_list ILSHIFT id ';'
                    | id_list IRSHIFT id ';'"""
        match p[2]:
            case "=":
                p[0] = ASTSetVar(p[1], p[3])
            case "+=":
                p[0] = ASTIaddVar(p[1], p[3])
            case "-=":
                p[0] = ASTIsubVar(p[1], p[3])
            case "/=":
                p[0] = ASTIdivVar(p[1], p[3])
            case "%=":
                p[0] = ASTImodVar(p[1], p[3])
            case "*=":
                p[0] = ASTImulVar(p[1], p[3])
            case "<<=":
                p[0] = ASTIlshiftVar(p[1], p[3])
            case ">>=":
                p[0] = ASTIrshiftVar(p[1], p[3])
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

    def p_astcase_start(self, p):
        """astcase : case '(' id ')' '{'"""
        p[0] = ASTCase(p[3], [])

    def p_astcase_code(self, p):
        """astcase : astcase expr_list ':' block_code"""
        p[0] = p[1]
        for i in p[2]:
            p[0].code.append((i, p[4]))

    def p_code_case(self, p):
        """code : astcase '}'"""
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
        p[0] = VarGetter(name=p[1])

    def p_id_index(self, p):
        """id   : id '[' INTEGER ']'"""
        p[0] = IndexGetter(getter=p[1], index=p[3])
