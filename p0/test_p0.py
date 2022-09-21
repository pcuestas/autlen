#!/usr/bin/env python

import re
import unittest

from regular_expressions import RE0, RE1, RE2, RE3, RE4, RE5


class TestP0(unittest.TestCase):
    """Tests of assignment 0."""

    def check_expression(self, expr: str, string: str, expected: bool) -> None:
        with self.subTest(string=string):
            match = re.fullmatch(expr, string)
            self.assertEqual(bool(match), expected)

    def test_exercise_0(self) -> None:
        self.check_expression(RE0, "a", True)
        self.check_expression(RE0, "bbbbaba", True)
        self.check_expression(RE0, "abbab", False)
        self.check_expression(RE0, "", False)

    def test_exercise_1(self) -> None:
        self.check_expression(RE1, "ab", True)
        self.check_expression(RE1, "ba", True)
        self.check_expression(RE1, "accb", True)
        self.check_expression(RE1, "bcca", True)
        self.check_expression(RE1, "bbcbbbca", True)
        self.check_expression(RE1, "acccaa", False)
        self.check_expression(RE1, "bcbbbc", False)
        self.check_expression(RE1, "abcaabbcca", True)
        self.check_expression(RE1, "ccc", False)
        self.check_expression(RE1, "", False)

    def test_exercise_2(self) -> None:
        self.check_expression(RE2, "2344", True)
        self.check_expression(RE2, "2344.", True)
        self.check_expression(RE2, "2344.0012", True)
        self.check_expression(RE2, "0.0012", True)
        self.check_expression(RE2, "0", True)
        self.check_expression(RE2, ".023", True)
        self.check_expression(RE2, "-2344", True)
        self.check_expression(RE2, "-2344.", True)
        self.check_expression(RE2, "-2344.0012", True)
        self.check_expression(RE2, "-0.0012", True)
        self.check_expression(RE2, "-0", False)
        self.check_expression(RE2, "-.023", True)
        self.check_expression(RE2, ".", False)
        self.check_expression(RE2, "", False)
        self.check_expression(RE2, "023", False)
        self.check_expression(RE2, "1.5e-7", False)

    def test_exercise_3(self) -> None:
        self.check_expression(RE3, "www.uam.es/", True)
        self.check_expression(RE3, "www.uam.es", False)
        self.check_expression(RE3, "www.uam.es//", False)
        self.check_expression(RE3, "moodle.uam.es/", True)
        self.check_expression(RE3, "moodle.uam.es", False)
        self.check_expression(RE3, "moodle.uam.es//", False)
        self.check_expression(RE3, "www.uam.es/hola/adios", True)
        self.check_expression(RE3, "moodle.uam.es/hola/adios/", True)

    def test_exercise_4(self) -> None:
        self.check_expression(RE4, "1+2+3+4", True)
        self.check_expression(RE4, "124/3+45*2-18", True)
        self.check_expression(RE4, "124/3+-45*2-18", False)
        self.check_expression(RE4, "23*0", False)
        self.check_expression(RE4, "0", False)
        self.check_expression(RE4, "", False)
        self.check_expression(RE4, "7*(3+12-36)", False)

    def test_exercise_5(self) -> None:
        self.check_expression(RE5, "1+2+3+4", True)
        self.check_expression(RE5, "124/3+45*2-18", True)
        self.check_expression(RE5, "124/3+-45*2-18", False)
        self.check_expression(RE5, "23*0", False)
        self.check_expression(RE5, "0", False)
        self.check_expression(RE5, "", False)
        self.check_expression(RE5, "7*(3+12-36)", True)
        self.check_expression(RE5, "7*(3+12-(2-5)/36)", False)


if __name__ == '__main__':
    unittest.main()
