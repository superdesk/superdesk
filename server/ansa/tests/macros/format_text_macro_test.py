# flake8: noqa: E501

import inspect
import unittest

from ansa.macros.format_text_width import format_text_macro


class LowercaseMacro(unittest.TestCase):

    maxDiff = None

    def test_format_text_macro(self):
        html = (
            "<p>Beautiful Soup offers a lot of tree-searching methods (covered below), "
            "and they mostly take the same arguments as find_all(): name, attrs, string, limit, "
            "and the keyword arguments.</p>"
            "<p>But the recursive argument is different: find_all() and find() are the only methods "
            "that support it. Passing recursive=False into a method like find_parents() wouldn’t be "
            "very useful.</p>"
        )

        new_html = inspect.cleandoc(
            """<p>Beautiful Soup offers a lot of tree-searching methods (covered
            below), and they mostly take the same arguments as find_all():
            name, attrs, string, limit, and the keyword arguments.</p><p>But the recursive argument is different: find_all() and find()
            are the only methods that support it. Passing recursive=False
            into a method like find_parents() wouldn’t be very useful.</p>"""
        )

        item = {"body_html": html}
        format_text_macro(item)
        self.assertEqual(item.get("body_html"), new_html)

        format_text_macro(item)
        self.assertEqual(item["body_html"], new_html)
