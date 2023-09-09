import os
import unittest
from unittest.mock import MagicMock, patch

from pyporter.pyporter import porter_creator

args = MagicMock()
args.configure_mock(type="python")
args.pkg = "oic"
args.pkgversion = "1.5.0"
args.arch = None
args.mirror = ""


class TestNoHomepageNone(unittest.TestCase):

    def setUp(self):
        try:
            self.f = open(os.path.join('tests', f'{__class__.__name__}.json'))
            self.data = self.f.read().encode()
        except FileNotFoundError as e:
            self.fail(f"Failed to open or read file: {e}")
        except Exception as e:
            self.fail(f"An error occurred: {e}")

    @patch('urllib.request.urlopen')
    def test_no_homepage_in_project_urls(self, m):
        cm = MagicMock()
        cm.read.return_value = self.data
        cm.__enter__.return_value = cm
        m.return_value = cm

        p = porter_creator(args)
        self.assertRaises(SystemExit, p.get_home)

    def tearDown(self):
        self.f.close()


class TestNoHomepageUseProjectUrl(unittest.TestCase):

    def setUp(self):
        self.f = open(os.path.join('tests', __class__.__name__ + '.json'))
        self.data = self.f.read().encode()

    @patch('urllib.request.urlopen')
    def test_no_homepage_in_project_urls(self, m):
        cm = MagicMock()
        cm.read.return_value = self.data
        cm.__enter__.return_value = cm
        m.return_value = cm

        p = porter_creator(args)
        self.assertEqual("test_project_url", p.get_home())

    def tearDown(self):
        self.f.close()


class TestNoHomepageUsePackageUrl(unittest.TestCase):

    def setUp(self):
        self.f = open(os.path.join('tests', __class__.__name__ + '.json'))
        self.data = self.f.read().encode()

    @patch('urllib.request.urlopen')
    def test_no_homepage_in_project_urls(self, m):
        cm = MagicMock()
        cm.read.return_value = self.data
        cm.__enter__.return_value = cm
        m.return_value = cm

        p = porter_creator(args)
        self.assertEqual("test_package_url", p.get_home())

    def tearDown(self):
        self.f.close()


class TestNoHomepageUseHomePage(unittest.TestCase):

    def setUp(self):
        self.f = open(os.path.join('tests', __class__.__name__ + '.json'))
        self.data = self.f.read().encode()

    @patch('urllib.request.urlopen')
    def test_no_homepage_in_project_urls(self, m):
        cm = MagicMock()
        cm.read.return_value = self.data
        cm.__enter__.return_value = cm
        m.return_value = cm

        p = porter_creator(args)
        self.assertEqual("test_home_page", p.get_home())

    def tearDown(self):
        self.f.close()


if __name__ == '__main__':
    unittest.main()
