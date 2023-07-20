import os
import unittest
from unittest.mock import MagicMock, patch

from pyporter.pyporter import porter_creator

SRC_URL = "https://files.pythonhosted.org/packages/d6/af/"\
        "3b4cfedd46b3addab52e84a71ab26518272c23c77116de3c61ead54af903/urllib3-2.0.3.tar.gz" # noqa


class TestPyprojectToml(unittest.TestCase):

    def setUp(self):
        self.f = open(os.path.join('tests', __class__.__name__ + '.json'))
        self.data = self.f.read().encode()

    @patch('urllib.request.urlopen')
    def test_pyprojecttoml(self, m):
        cm = MagicMock()
        cm.read.return_value = self.data
        cm.__enter__.return_value = cm
        m.return_value = cm

        args = MagicMock()
        args.configure_mock(type="python")
        args.pkg = "urllib3"
        args.pkgversion = "2.0.3"
        args.arch = None
        args.mirror = ""

        p = porter_creator(args)
        self.assertEqual("https://pypi.org/project/urllib3/", p.get_home())
        self.assertEqual(p.get_version(), "2.0.3")
        self.assertEqual(p.get_source_url(), SRC_URL)
        self.assertEqual(p.get_license(), "MIT License")
        self.assertEqual(p.get_requires(), [
            "(python3-brotli>=1.0.9)", "(python3-certifi)",
            "(python3-urllib3-secure-extra)",
            "(python3-pysocks<2.0 with python3-pysocks>=1.5.6)"
        ])

    def tearDown(self):
        self.f.close()


if __name__ == '__main__':
    unittest.main()
