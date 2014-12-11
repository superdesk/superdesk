
import os
import unittest

from .anpa import ANPAFileParser


def fixture(filename):
    dirname = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(dirname, 'fixtures', filename)


class ANPATestCase(unittest.TestCase):

    parser = ANPAFileParser()

    def open(self, filename):
        return self.parser.parse_file(fixture(filename))

    def test_open_anpa_file(self):
        item = self.open('anpa-1.tst')
        self.assertEqual('text', item['type'])
        self.assertEqual('2870', item['provider_sequence'])
        self.assertEqual('r', item['priority'])
        self.assertEqual('l', item['anpa-category']['qcode'])
        self.assertEqual('text', item['type'])
        self.assertEqual(1049, item['word_count'])
        self.assertEqual('For Argentine chemo patients, mirrors can hurt', item['headline'])
        self.assertEqual('By PAUL BYRNE and ALMUDENA CALATRAVA', item['byline'])
        self.assertRegex(item['body_text'], '^BUENOS')
        self.assertEqual('Argentina-Cancer', item['slugline'])
        self.assertEqual('2013-11-13T15:09:00+00:00', item['firstcreated'].isoformat())

    def test_ed_note(self):
        item = self.open('anpa-2.tst')
        self.assertEqual('This is part of an Associated Press investigation into the hidden costs of green energy.',
                         item['ednote'])

    def test_tab_content(self):
        item = self.open('anpa-3.tst')
        self.assertEqual('preformatted', item['type'])
