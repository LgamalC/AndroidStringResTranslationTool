import unittest

import unittest
from unittest.mock import MagicMock

from src.dayun.translator import escape_xml


class TestTranslator(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestTranslator, self).__init__(*args, **kwargs)

    def test_escape_content_given_quote_str_return_escaped_str(self):
        res = escape_xml('"test"')
        self.assertEqual("&quot;test&quot;",res)


