from typing import List


class ASTDeclaration:
    def __init__(self, name: str, default: int):
        self.default: int = default
        self.name: str = name

    def __str__(self):
        return f"int {self.name}={self.default}"


class ASTAssembler:
    def __init__(self, code: str):
        self.code: str = code

    def __str__(self):
        return f"asm({repr(self.code)})"


class ASTGoto:
    def __init__(self, name: str):
        self.name: str = name

    def __str__(self):
        return f"goto {self.name}"


class ASTFile:
    def __init__(self):
        self.declarations: List[ASTDeclaration] = []
        self.code = []
