# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license*.
from superdesk.io import register_feed_parser
from superdesk.io.feed_parsers import FileFeedParser
from superdesk.metadata.item import ITEM_TYPE, CONTENT_TYPE, FORMAT, FORMATS
from superdesk.utc import utcnow
from superdesk.errors import AlreadyExistsError
from io import StringIO
import uuid
import html
import logging


class TextFileParser(FileFeedParser):
    """
    The simplest parser for text files, it makes no assumptions about the contents, other than the first line
    is put into the headline
    """

    NAME = 'text_file'

    def can_parse(self, file_path):
        """
        Determines if the parser can likely be able to parse the file.
        :param file_path:
        :return:
        """
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                lines = f.readlines()
                if len(lines) > 0:
                    return True
                return False
        except Exception as ex:
            print(ex)
            return False

    def set_item_defaults(self, item, filename):
        """
        Set normal defaults in the item
        :param item:
        :param filename:
        :return:
        """
        item['urgency'] = 5
        item['pubstatus'] = 'usable'
        item['versioncreated'] = utcnow()
        item[ITEM_TYPE] = CONTENT_TYPE.TEXT
        item[FORMAT] = FORMATS.PRESERVED
        item['guid'] = filename + str(uuid.uuid4())

    def parse(self, filename, provider=None):
        """
        Attempt to parse the text file and return the item
        :param filename:
        :param provider:
        :return:
        """
        try:
            with open(filename, 'r', encoding='latin-1') as f:
                lines = f.readlines()
                item = {}

                self.set_item_defaults(item, filename)
                text = StringIO()
                if len(lines) > 0:
                    item['headline'] = lines[0].strip()
                for line in lines:
                    text.write(line)
                item['body_html'] = '<pre>' + html.escape(text.getvalue()) + '</pre>'
            return item
        except Exception as ex:
            logging.exception(ex)

try:
    register_feed_parser(TextFileParser.NAME, TextFileParser())
except AlreadyExistsError as ex:
    pass
