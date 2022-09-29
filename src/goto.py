class Goto:
    def __init__(self, name: str):
        self.name: str = name

    def __str__(self):
        return f"goto {self.name}"
