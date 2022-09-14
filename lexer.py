from ply import lex


class CodeLexer:
    keywords = (
        'while', 'if', 'elif', 'else', 'out', 'goto', 'asm', 'code', 'int',
    )
    tokens = keywords + (
        'INTEGER', 'STRING',
        'SET', 'LSBRACKET', 'RSBRACKET', 'LCBRACKET', 'RCBRACKET', 'LPARENTHESIS', 'RPARENTHESIS',
        'IADD', 'ISUB',
        'ID', 'NEWLINE',
    )

    t_ignore = ' \t'
    t_SET = r'='
    t_LSBRACKET = r'\['
    t_RSBRACKET = r'\]'
    t_LCBRACKET = r'\{'
    t_RCBRACKET = r'\}'
    t_LPARENTHESIS = r'\('
    t_RPARENTHESIS = r'\)'
    t_IADD = r'\+='
    t_ISUB = r'\-='

    def __init__(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)

    def t_STRING(self, t):
        r'\".*?\"'
        t.value = t.value[1:-1]
        if len(t.value) == 1:
            t.value = ord(t.value)
            t.type = 'INTEGER'
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
        return t

    def t_error(self, t):
        raise Exception("Illegal character %s" % t.value[0])

    def test(self, data):
        self.lexer.input(data)
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            print(tok)
