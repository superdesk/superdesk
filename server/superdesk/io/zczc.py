# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license*.

from superdesk.io import Parser
from superdesk.errors import ParserError
from .iptc import subject_codes
from superdesk.utc import utcnow
import uuid


class ZCZCParser(Parser):
    """
    It is expected that the stories contained in the files will be framed by the strings
    ZCZC

    NNNN

    * the NNNN is optional
    """
    START_OF_MESSAGE = 'ZCZC'
    END_OF_MESSAGE = 'NNNN'

    CATEGORY = '$'
    KEYWORD = ':'
    TAKEKEY = '='
    HEADLINE = '^'
    # *format "X" text "T" tabular
    FORMAT = '*'
    # &service level - Default A but for results should match category
    SERVICELEVEL = '&'
    # +IPTC Subject Reference Number as defined in the SubjectReference.ini file
    IPTC = '+'

    # Posible values for formsat
    TEXT = 'X'
    TABULAR = 'T'

    header_map = {KEYWORD: 'slugline', TAKEKEY: 'anpa_take_key',
                  HEADLINE: 'headline', SERVICELEVEL: None}

    def can_parse(self, filestr):
        return self.START_OF_MESSAGE in filestr

    def parse_file(self, filename, provider):
        try:
            item = {}
            self.set_item_defaults(item)

            with open(filename, 'r', encoding='ascii') as f:
                lines = f.readlines()
                header = False
                for line in lines:
                    if self.START_OF_MESSAGE in line and not header:
                        item['guid'] = filename + str(uuid.uuid4())
                        header = True
                        continue
                    if header:
                        if line[0] in self.header_map:
                            if self.header_map[line[0]]:
                                item[self.header_map[line[0]]] = line[1:-1]
                            continue
                        if line[0] == self.CATEGORY:
                            item['anpa_category'] = [{'qcode': line[1]}]
                            continue
                        if line[0] == self.FORMAT:
                            if line[1] == self.TEXT:
                                item['type'] = 'text'
                                continue
                            if line[1] == self.TABULAR:
                                item['type'] = 'preformatted'
                                continue
                            continue
                        if line[0] == self.IPTC:
                            iptc_code = line[1:-1]
                            item['subject'] = [{'qcode': iptc_code, 'name': subject_codes[iptc_code]}]
                            continue
                        header = False
                        item['body_html'] = line
                    else:
                        if self.END_OF_MESSAGE in line:
                            break
                        item['body_html'] = item['body_html'] + line
            return item

        except Exception as ex:
            raise ParserError.ZCZCParserError(ex, provider)

    def set_item_defaults(self, item):
        item['type'] = 'text'
        item['urgency'] = 5
        item['pubstatus'] = 'usable'
        item['versioncreated'] = utcnow()
