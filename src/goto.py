from code_getters import IGetter


class Goto:
    def __init__(self, var: IGetter):
        self.var: IGetter = var
