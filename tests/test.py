import random
from operator import eq
from unittest import TestCase

from src import compile_code
from tests.interpreter import Interpreter


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
        out = Interpreter()(compile_code(code), inp)
        self.assertTrue(all(map(eq, out, reversed(inp))))

    def test_add_int(self):
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
        out = Interpreter()(compile_code(code), inp)
        self.assertEqual((left1 + right1) % 256, out[0])
        self.assertEqual((left2 + right2) % 256, out[1])

    def test_sub_int(self):
        inp = b""
        left1 = random.randint(0, 255)
        right1 = random.randint(0, 255)
        left2 = random.randint(0, 255)
        right2 = random.randint(0, 255)
        code = f"""
            int a = {left1};
            int b = {left2};
            a -= {right1};
            b -= {right2};
            out a;
            out b;
                """
        out = Interpreter()(compile_code(code), inp)
        self.assertEqual((left1 - right1 + 256) % 256, out[0])
        self.assertEqual((left2 - right2 + 256) % 256, out[1])

    def test_set_int(self):
        inp = b""
        left1 = random.randint(0, 255)
        right1 = random.randint(0, 255)
        left2 = random.randint(0, 255)
        right2 = random.randint(0, 255)
        code = f"""
            int a = {left1};
            int b = {left2};
            a = {right1};
            b = {right2};
            out a;
            out b;
                """
        out = Interpreter()(compile_code(code), inp)
        self.assertEqual(right1, out[0])
        self.assertEqual(right2, out[1])

    def test_mul_int(self):
        inp = b""
        left1 = random.randint(0, 255)
        right1 = random.randint(1, 255)
        left2 = random.randint(0, 255)
        right2 = random.randint(1, 255)
        code = f"""
            int a = {left1};
            int b = {left2};
            a *= {right1};
            b *= {right2};
            out a;
            out b;
                """
        out = Interpreter(1)(compile_code(code), inp)
        self.assertEqual((left1 * right1) % 256, out[0])
        self.assertEqual((left2 * right2) % 256, out[1])

    def test_mul_zero_int(self):
        inp = b""
        left1 = random.randint(0, 255)
        right1 = 0
        left2 = random.randint(0, 255)
        right2 = 0
        code = f"""
            int a = {left1};
            int b = {left2};
            a *= {right1};
            b *= {right2};
            out a;
            out b;
                """
        out = Interpreter(1)(compile_code(code), inp)
        self.assertEqual((left1 * right1) % 256, out[0])
        self.assertEqual((left2 * right2) % 256, out[1])

    def test_div_int(self):
        inp = b""
        left1 = random.randint(0, 255)
        right1 = random.randint(1, 255)
        left2 = random.randint(0, 255)
        right2 = random.randint(1, 255)
        code = f"""
            int a = {left1};
            int b = {left2};
            a /= {right1};
            b /= {right2};
            out a;
            out b;
                """
        out = Interpreter(1)(compile_code(code), inp)
        self.assertEqual((left1 // right1) % 256, out[0])
        self.assertEqual((left2 // right2) % 256, out[1])

    def test_div_zero_int(self):
        inp = b""
        left1 = random.randint(0, 255)
        right1 = 0
        left2 = random.randint(0, 255)
        right2 = 0
        code = f"""
            int a = {left1};
            int b = {left2};
            a /= {right1};
            b /= {right2};
            out a;
            out b;
                """
        out = Interpreter(1)(compile_code(code), inp)
        self.assertEqual(255, out[0])
        self.assertEqual(255, out[1])

    def test_mod_int(self):
        inp = b""
        left1 = random.randint(0, 255)
        right1 = random.randint(1, 255)
        left2 = random.randint(0, 255)
        right2 = random.randint(1, 255)
        code = f"""
            int a = {left1};
            int b = {left2};
            a %= {right1};
            b %= {right2};
            out a;
            out b;
                """
        out = Interpreter(1)(compile_code(code), inp)
        self.assertEqual(left1 % right1, out[0])
        self.assertEqual(left2 % right2, out[1])

    def test_mod_zero_int(self):
        inp = b""
        left1 = random.randint(0, 255)
        right1 = 0
        left2 = random.randint(0, 255)
        right2 = 0
        code = f"""
            int a = {left1};
            int b = {left2};
            a %= {right1};
            b %= {right2};
            out a;
            out b;
                """
        out = Interpreter(1)(compile_code(code), inp)
        self.assertEqual(255, out[0])
        self.assertEqual(255, out[1])

    def test_add_var(self):
        inp = b""
        left1 = random.randint(0, 255)
        right1 = random.randint(0, 255)
        left2 = random.randint(0, 255)
        right2 = random.randint(0, 255)
        code = f"""
                    int a = {left1};
                    int b = {left2};
                    int c = {right1};
                    int d = {right2};
                    a += c;
                    b += d;
                    out a;
                    out b;
                        """
        out = Interpreter()(compile_code(code), inp)
        self.assertEqual((left1 + right1) % 256, out[0])
        self.assertEqual((left2 + right2) % 256, out[1])

    def test_sub_var(self):
        inp = b""
        left1 = random.randint(0, 255)
        right1 = random.randint(0, 255)
        left2 = random.randint(0, 255)
        right2 = random.randint(0, 255)
        code = f"""
                    int a = {left1};
                    int b = {left2};
                    int c = {right1};
                    int d = {right2};
                    a -= c;
                    b -= d;
                    out a;
                    out b;
                        """
        out = Interpreter()(compile_code(code), inp)
        self.assertEqual((left1 - right1 + 256) % 256, out[0])
        self.assertEqual((left2 - right2 + 256) % 256, out[1])

    def test_set_var(self):
        inp = b""
        left1 = random.randint(0, 255)
        right1 = random.randint(0, 255)
        left2 = random.randint(0, 255)
        right2 = random.randint(0, 255)
        code = f"""
                    int a = {left1};
                    int b = {left2};
                    int c = {right1};
                    int d = {right2};
                    a = c;
                    b = d;
                    out a;
                    out b;
                        """
        out = Interpreter()(compile_code(code), inp)
        self.assertEqual(right1, out[0])
        self.assertEqual(right2, out[1])

    def test_cat_program(self):
        inp = random.randbytes(10) + b"\n"
        code = r"""
            int a = 1;
            while(a){
                in a;
                out a;
                a -= "\n";
            }
            """
        out = Interpreter()(compile_code(code), inp)
        self.assertEqual(inp, out)

    def test_while_true(self):
        inp = b""
        code = r"""
            int a = "1";
            while(a){
                out a;
            }
            """
        inter = Interpreter()
        with self.assertRaises(TimeoutError):
            inter(compile_code(code), inp)
        self.assertTrue(len(inter.out) > 100)
