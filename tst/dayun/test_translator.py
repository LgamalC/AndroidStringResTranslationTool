import os
import shutil
import tempfile
import unittest
from unittest.mock import MagicMock


from src.dayun.translator import escape_xml, ResourceFinder


class TestTranslator(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestTranslator, self).__init__(*args, **kwargs)

    def test_escape_content_given_quote_str_return_escaped_str(self):
        res = escape_xml('"test"')
        self.assertEqual("&quot;test&quot;", res)

    def test_get_locale_files_from_dir(self):
        testResourceFinder = ResourceFinder()

        abs_file_path = os.path.abspath(__file__)
        abs_file_dir = os.path.dirname(abs_file_path)
        test_data_dir = os.path.join(abs_file_dir, '..', '..', 'test_data', 'app', 'src', 'main', 'res')
        test = testResourceFinder.get_locale_files_from_dir(test_data_dir, 'xml')
        self.assertEqual(2, len(test))

