
import unittest
from .topics import get_topics


class TopicTestCase(unittest.TestCase):

    def test_get_topics(self):
        topics = get_topics()
        self.assertGreater(len(topics), 100)
        self.assertEqual('Accident', topics['patopic:ACCIDENT'])
