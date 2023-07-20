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


if __name__ == '__main__':
    unittest.main()
