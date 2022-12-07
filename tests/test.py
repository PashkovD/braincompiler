import random
from operator import eq
from unittest import TestCase

from tests.interpreter import Interpreter


class Tests(TestCase):
    from braincompiler import compile_code
    compile_code = staticmethod(compile_code)

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
        print(code)
        print(inp)
        out = Interpreter()(self.compile_code(code), inp)
        print(out)
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
        print(code)
        print(inp)
        out = Interpreter()(self.compile_code(code), inp)
        print(out)
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
        print(code)
        print(inp)
        out = Interpreter()(self.compile_code(code), inp)
        print(out)
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
        print(code)
        print(inp)
        out = Interpreter()(self.compile_code(code), inp)
        print(out)
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
        print(code)
        print(inp)
        out = Interpreter()(self.compile_code(code), inp)
        print(out)
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
        print(code)
        print(inp)
        out = Interpreter()(self.compile_code(code), inp)
        print(out)
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
        print(code)
        print(inp)
        out = Interpreter()(self.compile_code(code), inp)
        print(out)
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
        print(code)
        print(inp)
        out = Interpreter()(self.compile_code(code), inp)
        print(out)
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
        print(code)
        print(inp)
        out = Interpreter()(self.compile_code(code), inp)
        print(out)
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
        print(code)
        print(inp)
        out = Interpreter()(self.compile_code(code), inp)
        print(out)
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
        print(code)
        print(inp)
        out = Interpreter()(self.compile_code(code), inp)
        print(out)
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
        print(code)
        print(inp)
        out = Interpreter()(self.compile_code(code), inp)
        print(out)
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
        print(code)
        print(inp)
        out = Interpreter()(self.compile_code(code), inp)
        print(out)
        self.assertEqual(right1, out[0])
        self.assertEqual(right2, out[1])

    def test_div_var(self):
        inp = b""
        left1 = random.randint(0, 255)
        right1 = random.randint(1, 255)
        left2 = random.randint(0, 255)
        right2 = random.randint(1, 255)
        code = f"""
            int a = {left1};
            int b = {left2};
            int c = {right1};
            int d = {right2};
            a /= c;
            b /= d;
            out a;
            out b;
        """
        print(code)
        print(inp)
        out = Interpreter()(self.compile_code(code), inp)
        print(out)
        self.assertEqual((left1 // right1) % 256, out[0])
        self.assertEqual((left2 // right2) % 256, out[1])

    def test_div_zero_var(self):
        inp = b""
        left1 = random.randint(0, 255)
        right1 = 0
        left2 = random.randint(0, 255)
        right2 = 0
        code = f"""
            int a = {left1};
            int b = {left2};
            int c = {right1};
            int d = {right2};
            a /= c;
            b /= d;
            out a;
            out b;
        """
        print(code)
        print(inp)
        out = Interpreter()(self.compile_code(code), inp)
        print(out)
        self.assertEqual(255, out[0])
        self.assertEqual(255, out[1])

    def test_mod_var(self):
        inp = b""
        left1 = random.randint(0, 255)
        right1 = random.randint(1, 255)
        left2 = random.randint(0, 255)
        right2 = random.randint(1, 255)
        code = f"""
            int a = {left1};
            int b = {left2};
            int c = {right1};
            int d = {right2};
            a %= c;
            b %= d;
            out a;
            out b;
        """
        print(code)
        print(inp)
        out = Interpreter()(self.compile_code(code), inp)
        print(out)
        self.assertEqual((left1 % right1) % 256, out[0])
        self.assertEqual((left2 % right2) % 256, out[1])

    def test_mod_zero_var(self):
        inp = b""
        left1 = random.randint(0, 255)
        right1 = 0
        left2 = random.randint(0, 255)
        right2 = 0
        code = f"""
            int a = {left1};
            int b = {left2};
            int c = {right1};
            int d = {right2};
            a %= c;
            b %= d;
            out a;
            out b;
        """
        print(code)
        print(inp)
        out = Interpreter()(self.compile_code(code), inp)
        print(out)
        self.assertEqual(255, out[0])
        self.assertEqual(255, out[1])

    def test_list_set_var(self):
        inp = random.randbytes(256)
        inp2 = random.randbytes(32)
        code = f"""
            string data = "{" " * 256}";
            int counter = 255;
            int var;""" + """
            while (counter){
                in var;
                data[counter] = var;
                counter -= 1;
            }
            in var;
            data[counter] = var;
            var = " ";
            
            counter = 32;
            while (counter){
                counter -= 1;
                in var;
                var = data[var];
                out var;
            }
            
        """
        print(code)
        print(repr(inp))
        print(repr(inp2))
        out = Interpreter(5)(self.compile_code(code), bytes(reversed(inp)) + inp2)
        print(out)
        self.assertEqual(len(inp2), len(out))
        for i, f in zip(inp2, out):
            self.assertEqual(inp[i], f)

    def test_cat_program(self):
        inp = random.randbytes(10)
        while inp.count(b"\n") != 0:
            inp = random.randbytes(10)
        inp += b"\n"
        code = r"""
            int a = 1;
            while(a){
                in a;
                out a;
                a -= "\n";
            }
            """
        print(code)
        print(inp)
        out = Interpreter()(self.compile_code(code), inp)
        print(out)
        self.assertEqual(inp, out)

    def test_while_true(self):
        inp = b""
        code = r"""
            int a = "1";
            while(a){
                out a;
            }
            """
        print(code)
        print(inp)
        inter = Interpreter()
        with self.assertRaises(TimeoutError):
            inter(self.compile_code(code), inp)
        print(f"{repr(inter.out[0])} * {len(inter.out)}")
        self.assertTrue(len(inter.out) > 100)
