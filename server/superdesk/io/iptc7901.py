# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


import re
from superdesk.errors import ParserError
from superdesk.io import Parser
from apps.archive.archive_media import generate_guid, GUID_TAG
from superdesk.utc import utcnow


class Iptc7901FileParser(Parser):
    """IPTC 7901 file parser"""

    def parse_file(self, filename):
        """Parse 7901 file by given filename.

        :param filename
        """
        try:
            item = {'type': 'preformatted'}
            item['guid'] = generate_guid(type=GUID_TAG)
            item['versioncreated'] = utcnow()

            with open(filename, 'rb') as f:
                lines = [line for line in f]
            # parse first header line
            m = re.match(b'\x01([a-zA-Z]*)([0-9]*) (.) (.) ([0-9]*) ([a-zA-Z0-9 ]*)', lines[0], flags=re.I)
            if m:
                item['original_source'] = m.group(1).decode()
                item['ingest_provider_sequence'] = m.group(2).decode()
                item['priority'] = self.map_priority(m.group(3).decode())
                item['anpa_category'] = [{'qcode': self.map_category(m.group(4).decode())}]
                item['word_count'] = int(m.group(5).decode())

            inHeader = True
            inText = False
            inNote = False
            for line in lines[1:]:
                # STX starts the body of the story
                if line[0:1] == b'\x02':
                    # pick the rest of the line off as the headline
                    item['headline'] = line[1:].decode().rstrip('\r\n')
                    item['body_html'] = ''
                    inText = True
                    inHeader = False
                    continue
                # ETX denotes the end of the story
                if line[0:1] == b'\x03':
                    break
                if inText:
                    if line.decode().find('The following information is not for publication') != -1:
                        inNote = True
                        inText = False
                        item['ednote'] = ''
                        continue
                    item['body_html'] += line.decode()
                if inNote:
                    item['ednote'] += line.decode()
                    continue
                if inHeader:
                    if 'slugline' not in item:
                        item['slugline'] = ''
                    item['slugline'] += line.decode().rstrip('/\r\n')
                    continue

            return item
        except Exception as ex:
            raise ParserError.IPTC7901ParserError(filename, ex)

    def map_priority(self, source_priority):
        if source_priority == '1':
            return 'B'
        elif source_priority == '2':
            return 'B'
        elif source_priority == '3':
            return 'U'
        elif source_priority == '4':
            return 'R'
        elif source_priority == '5':
            return 'D'
        else:
            return 'R'

    def map_category(self, source_category):
        if source_category == 'x' or source_category == 'X':
            return 'i'
        else:
            return source_category
