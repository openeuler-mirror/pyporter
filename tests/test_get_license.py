import os
import unittest
from unittest.mock import MagicMock, patch

from pyporter.pyporter import porter_creator


class TestNoOSIApproved(unittest.TestCase):
    """
    case 1: json["info"]["license"] == "" and the License in json["info"]["classifiers"] is not OSI approved
    """

    def setUp(self):
        self.f = open(os.path.join('tests', __class__.__name__ + '.json'))
        self.data = self.f.read().encode()

    @patch('urllib.request.urlopen')
    def test_no_OSI_approved(self, m):
        cm = MagicMock()
        cm.read.return_value = self.data
        cm.__enter__.return_value = cm
        m.return_value = cm

        args = MagicMock()
        args.configure_mock(type="python")
        args.pkg = "oic"
        args.pkgversion = "1.5.0"
        args.arch = None
        args.mirror = ""

        p = porter_creator(args)
        self.assertEqual(
            'CC0 1.0 Universal (CC0 1.0) Public Domain Dedication',
            p.get_license())

    def tearDown(self):
        self.f.close()


class TestOSIApproved(unittest.TestCase):
    """
    case 2: json["info"]["license"] == "" and the License in json["info"]["classifiers"] is OSI approved
    """

    def setUp(self):
        self.f = open(os.path.join('tests', __class__.__name__ + '.json'))
        self.data = self.f.read().encode()

    @patch('urllib.request.urlopen')
    def test_OSI_approved(self, m):
        cm = MagicMock()
        cm.read.return_value = self.data
        cm.__enter__.return_value = cm
        m.return_value = cm

        args = MagicMock()
        args.configure_mock(type="python")
        args.pkg = "oic"
        args.pkgversion = "1.5.0"
        args.arch = None
        args.mirror = ""

        p = porter_creator(args)
        self.assertEqual('Apache Software License', p.get_license())

    def tearDown(self):
        self.f.close()


class TestLicense(unittest.TestCase):
    """
    case 3: json["info"]["license"] != ""
    """

    def setUp(self):
        self.f = open(os.path.join('tests', __class__.__name__ + '.json'))
        self.data = self.f.read().encode()

    @patch('urllib.request.urlopen')
    def test_OSI_approved(self, m):
        cm = MagicMock()
        cm.read.return_value = self.data
        cm.__enter__.return_value = cm
        m.return_value = cm

        args = MagicMock()
        args.configure_mock(type="python")
        args.pkg = "oic"
        args.pkgversion = "1.5.0"
        args.arch = None
        args.mirror = ""

        p = porter_creator(args)
        self.assertEqual('Apache 2.0', p.get_license())

    def tearDown(self):
        self.f.close()


class TestNoLicense(unittest.TestCase):
    """
    case 4: json["info"]["license"] = ""
    """

    def setUp(self):
        self.f = open(os.path.join('tests', __class__.__name__ + '.json'))
        self.data = self.f.read().encode()

    @patch('urllib.request.urlopen')
    def test_OSI_approved(self, m):
        cm = MagicMock()
        cm.read.return_value = self.data
        cm.__enter__.return_value = cm
        m.return_value = cm

        args = MagicMock()
        args.configure_mock(type="python")
        args.pkg = "oic"
        args.pkgversion = "1.5.0"
        args.arch = None
        args.mirror = ""

        p = porter_creator(args)
        self.assertEqual('UNKNOWN', p.get_license())


if __name__ == '__main__':
    unittest.main()
