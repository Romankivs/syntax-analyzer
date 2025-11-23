import unittest
import sys

class ParserError(Exception):
    pass

class Parser:
    def __init__(self, text):
        self.text = text
        self.pos = 0

    def current(self):
        if self.pos >= len(self.text):
            return None
        return self.text[self.pos]

    def consume(self, ch=None):
        if self.pos >= len(self.text):
            raise ParserError(f"Unexpected end of input, expected '{ch}'")

        current = self.text[self.pos]
        if ch is not None and current != ch:
            raise ParserError(f"Expected '{ch}', got '{current}' at pos {self.pos}")

        self.pos += 1
        return current

    # <дужки> ::= <квадратні> | <круглі>
    def parse_brackets(self):
        c = self.current()
        if c in ('B', '['):
            return self.parse_square()
        elif c in ('A', '('):
            return self.parse_round()
        else:
            raise ParserError(f"Unexpected symbol '{c}' at pos {self.pos}")

    # <квадратні> ::= 'B'
    #               | '[[' <квадратні> ']' '(' <круглі> ')' ']'
    def parse_square(self):
        c = self.current()
        if c == 'B':
            self.consume('B')
            return "SQ(A)"

        self.consume('[')
        self.consume('[')

        left = self.parse_square()

        self.consume(']')
        self.consume('(')

        right = self.parse_round()

        self.consume(')')
        self.consume(']')

        return f"SQ({left},{right})"

    # <круглі> ::= 'A'
    #            | '(' '(' <круглі> ')' '[' <квадратні> ']' ')'
    def parse_round(self):
        c = self.current()
        if c == 'A':
            self.consume('A')
            return "RD(A)"

        self.consume('(')
        self.consume('(')

        inner = self.parse_round()

        self.consume(')')
        self.consume('[')

        sq = self.parse_square()

        self.consume(']')
        self.consume(')')

        return f"RD({inner},{sq})"

def parse_expression(expr):
    parser = Parser(expr)
    result = parser.parse_brackets()

    if parser.current() is not None:
        raise ParserError(f"Extra characters after valid expression at pos {parser.pos}")

    return result

class TestParser(unittest.TestCase):

    # -------- VALID CASES --------
    def test_atom_square(self):
        self.assertEqual(parse_expression("B"), "SQ(A)")

    def test_atom_round(self):
        self.assertEqual(parse_expression("A"), "RD(A)")

    def test_simple_square(self):
        self.assertEqual(parse_expression("[[B](A)]"), "SQ(SQ(A),RD(A))")

    def test_simple_round(self):
        self.assertEqual(parse_expression("((A)[B])"), "RD(RD(A),SQ(A))")

    def test_nested_valid1(self):
        expr = "[[B](((A)[B]))]"
        self.assertEqual(
            parse_expression(expr),
            "SQ(SQ(A),RD(RD(A),SQ(A)))"
        )

    def test_nested_valid2(self):
        expr = "((A)[[[B](A)]])"
        self.assertEqual(
            parse_expression(expr),
            "RD(RD(A),SQ(SQ(A),RD(A)))"
        )

    # -------- INVALID --------

    def test_invalid_symbol(self):
        with self.assertRaises(ParserError):
            parse_expression("X")

    def test_missing_end_square(self):
        with self.assertRaises(ParserError):
            parse_expression("[[B](A)")

    def test_missing_end_round(self):
        with self.assertRaises(ParserError):
            parse_expression("((A)[B]")

    def test_invalid_mixed_square(self):
        with self.assertRaises(ParserError):
            parse_expression("[[A](B)]")

    def test_invalid_round_structure(self):
        with self.assertRaises(ParserError):
            parse_expression("((B)[A])")

    def test_empty(self):
        with self.assertRaises(ParserError):
            parse_expression("")

    def test_unexpected_after_valid(self):
        with self.assertRaises(ParserError):
            parse_expression("AA")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        expr = sys.argv[1]
        try:
            print(expr)
            result = parse_expression(expr)
            print(f"Parsed result: {result}")
        except ParserError as e:
            print(f"ParserError: {e}")
    else:
        unittest.main()
