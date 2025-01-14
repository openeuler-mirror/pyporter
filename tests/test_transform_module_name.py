import unittest

from pyporter.utils import transform_module_name


class TestTransofrmModuleName(unittest.TestCase):

    def test_transform_module_name(self):
        input_str = "brotli>=1.0.9"
        expected_output = "(python3-brotli>=1.0.9)"
        self.assertEqual(transform_module_name(input_str), expected_output)

        input_str = "pysocks<2.0,>=1.5.6"
        expected_output = "(python3-pysocks<2.0 with python3-pysocks>=1.5.6)"
        self.assertEqual(transform_module_name(input_str), expected_output)

    def test_transform_module_name_strip_whitespace(self):
        input_str = "pyjwkest (>=1.3.6)"
        expected_output = "(python3-pyjwkest>=1.3.6)"
        self.assertEqual(transform_module_name(input_str), expected_output)

        input_str = "ipython[all] (=3.1)"
        expected_output = "(python3-ipython[all]=3.1)"
        self.assertEqual(transform_module_name(input_str), expected_output)

    def test_invalid_input(self):
        input_str = "!invalid_module123"
        expected_output = "Invalid input format"
        self.assertEqual(transform_module_name(input_str), expected_output)


if __name__ == '__main__':
    unittest.main()
