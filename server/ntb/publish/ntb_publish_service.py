# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2016 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from superdesk.publish.publish_service import PublishService, set_publish_service
from xml.etree import ElementTree as ET
import logging
logger = logging.getLogger(__name__)


class NTBPublishService(PublishService):
    DEFAULT_EXT = "xml"

    @classmethod
    def get_filename(cls, item):
        # we reparse formatted item to get filename from <meta name="filename"> element
        # this way we are sure that we have the exact same filename
        try:
            xml = ET.fromstring(item['formatted_item'])
        except (KeyError, ET.ParseError):
            filename = None
        else:
            filename = xml.find('head/meta[@name="filename"]').attrib['content']
        if not filename:
            return super(NTBPublishService, cls).get_filename(item)
        return filename


set_publish_service(NTBPublishService)
