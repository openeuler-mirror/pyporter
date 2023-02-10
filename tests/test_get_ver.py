import unittest
from pyporter.pyporter import porter_creator


class TestGetByVer(unittest.TestCase):
    def test_invalid_ver(self):
        self.assertRaises(SystemExit, porter_creator, "python", None, "oic", "3.11.1")

    def test_valid_ver(self):
        p = porter_creator("python", None, "oic", "1.5.0")
        self.assertEqual(p.get_version(), "1.5.0")


if __name__ == '__main__':
    unittest.main()
