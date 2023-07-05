import unittest
from unittest.mock import MagicMock

from pyporter.pyporter import porter_creator

VALID_PKG = ["pure-eval", "oic", "XStatic-Patternfly"]
VALID_ARCHIVE_NAME = ["pure_eval", "oic", "XStatic-Patternfly"]


class TestValidArchive(unittest.TestCase):

    def test(self):
        args = MagicMock()
        args.configure_mock(type="python")
        args.pkgversion = ""
        args.arch = None
        args.mirror = ""

        for i, pkg in enumerate(VALID_PKG):
            args.pkg = pkg
            p = porter_creator(args)
            self.assertEqual(p.get_archive_name(), VALID_ARCHIVE_NAME[i])


if __name__ == '__main__':
    unittest.main()
