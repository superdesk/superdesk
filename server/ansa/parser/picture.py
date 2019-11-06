
import os
from superdesk.io.feed_parsers.image_iptc import ImageIPTCFeedParser


class PictureParser(ImageIPTCFeedParser):
    """Use filename for guid."""

    def parse_item(self, image_path):
        item = super().parse_item(image_path)
        item['guid'] = item['uri'] = os.path.basename(image_path)
        return item
