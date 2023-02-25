import unittest
from pyporter.pyporter import porter_creator

SRC_URL = "https://files.pythonhosted.org/packages/36/62/7cda20a9bd8c52bf47c6f1cf7e"\
         "019df7e6cd2aed3b147a786d087a848305/oic-1.5.0.tar.gz"
MIRROR_URL = "https://mirrors.aliyun.com/pypi/packages/36/62/7cda20a9bd8c52bf47c6f1c"\
            "f7e019df7e6cd2aed3b147a786d087a848305/oic-1.5.0.tar.gz"


class TestValidSource(unittest.TestCase):
    def test_no_mirror(self):
        p = porter_creator('python', None, "oic", "1.5.0")
        self.assertEqual(p.get_source_url(), SRC_URL)

    def test_valid_mirror(self):
        p = porter_creator('python', None, "oic", "1.5.0", "https://mirrors.aliyun.com/pypi")
        self.assertEqual(p.get_source_url(), MIRROR_URL)


if __name__ == '__main__':
    unittest.main()
