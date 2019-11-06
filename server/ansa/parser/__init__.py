
from .parser import ANSAParser
from .picture import PictureParser
from superdesk.io.registry import registered_feed_parsers

registered_feed_parsers[ANSAParser.NAME] = ANSAParser()
registered_feed_parsers[PictureParser.NAME] = PictureParser()
