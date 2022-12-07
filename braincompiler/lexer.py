from ply import lex


class CodeLexer:
    keywords = (
        'while', 'if', 'elif', 'else', 'in', 'out', 'goto', 'asm', 'int', 'string', 'case'
    )
    tokens = keywords + (
        'INTEGER', 'STRING',
        'IADD', 'ISUB', 'IDIV', 'IMOD', 'IMUL', 'ILSHIFT', 'IRSHIFT',
        'ID', 'NEWLINE', 'DEFINE',
    )
    literals = ['=', '+', '-', '(', ')', '{', '}', '[', ']', ',', ';', '*', ':']

    t_ignore = ' \t'
    t_ignore_COMMENT = r'\#.*'
    t_IADD = r'\+='
    t_ISUB = r'\-='
    t_IDIV = r'\/='
    t_IMOD = r'\%='
    t_IMUL = r'\*='
    t_ILSHIFT = r'<<='
    t_IRSHIFT = r'>>='
    t_DEFINE = r'\#define'

    def __init__(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)

    def t_STRING(self, t):
        r'\".*?\"'
        import ast
        t.value = ast.literal_eval("b" + t.value)
        return t

    def t_ID(self, t):
        r'[A-Za-z_][A-Za-z0-9_]*'
        if t.value in self.keywords:
            t.type = t.value
        return t

    def t_INTEGER(self, t):
        r'\d+'
        t.value = int(t.value)
        return t

    def t_NEWLINE(self, t):
        r'\n+'
        t.lexer.lineno += t.value.count("\n")
        # return t

    def t_error(self, t):
        raise Exception(f"[:{t.lineno}]Illegal character {t.value[0]}")

    def test(self, data):
        self.lexer.input(data)
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            print(tok)
