
from .parser import ANSAParser
from superdesk.io.registry import registered_feed_parsers

registered_feed_parsers[ANSAParser.NAME] = ANSAParser()
