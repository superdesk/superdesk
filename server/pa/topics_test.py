
import unittest
from .topics import get_topics


class TopicTestCase(unittest.TestCase):

    def test_get_topics(self):
        topics = get_topics()
        self.assertEqual(321, len(topics))
        self.assertEqual('Accident', topics['patopic:ACCIDENT'])
