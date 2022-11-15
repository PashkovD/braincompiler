import random
from operator import eq
from unittest import TestCase

import tests.intepreter
from src import compile_code


class Tests(TestCase):
    def test_2_in_reverse_out(self):
        inp = random.randbytes(2)
        code = """
            int a;
            int b;
            in a;
            in b;
            out b;
            out a;
        """
        out = tests.intepreter.process(compile_code(code), inp)
        self.assertTrue(all(map(eq, out, reversed(inp))))

    def test_add_const(self):
        inp = b""
        left1 = random.randint(0, 255)
        right1 = random.randint(0, 255)
        left2 = random.randint(0, 255)
        right2 = random.randint(0, 255)
        code = f"""
            int a = {left1};
            int b = {left2};
            a += {right1};
            b += {right2};
            out a;
            out b;
                """
        out = tests.intepreter.process(compile_code(code), inp)
        self.assertEqual((left1 + right1) % 256, out[0])
        self.assertEqual((left2 + right2) % 256, out[1])