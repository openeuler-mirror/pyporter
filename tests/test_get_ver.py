import unittest
from unittest.mock import MagicMock

from pyporter.pyporter import porter_creator


class TestGetByVer(unittest.TestCase):

    def test_invalid_ver(self):
        args = MagicMock()
        args.configure_mock(type="python")
        args.pkg = "oic"
        args.pkgversion = "0.0.0"
        args.arch = None
        args.mirror = ""

        self.assertRaises(SystemExit, porter_creator, args)

    def test_valid_ver(self):
        args = MagicMock()
        args.configure_mock(type="python")
        args.pkg = "oic"
        args.pkgversion = "1.5.0"
        args.arch = None
        args.mirror = ""

        p = porter_creator(args)
        self.assertEqual(p.get_version(), "1.5.0")


if __name__ == '__main__':
    unittest.main()
