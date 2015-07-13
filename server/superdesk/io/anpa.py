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
from datetime import datetime
from superdesk.utc import utc
from superdesk.errors import ParserError
from superdesk.io import Parser


class ANPAFileParser(Parser):
    """ANPA 1312 file parser"""

    def parse_file(self, filename):
        """Parse anpa file by given filename.

        :param filename
        """
        try:
            item = {'type': 'text'}

            with open(filename, 'rb') as f:
                lines = [line for line in f]

            # parse first header line
            m = re.match(b'\x16\x16\x01([a-z])([0-9]{4})\x1f([a-z-]+)', lines[0], flags=re.I)
            if m:
                item['provider_sequence'] = m.group(2).decode()

            # parse second header line
            m = re.match(
                b'([a-z]) ([a-z])(\x13|\x14)(\x11|\x12) (am-|pm-|bc-)([a-z-]+)(.*) '
                b'([0-9]{1,2})-([0-9]{1,2}) ([0-9]{4})',
                lines[1], flags=re.I)
            if m:
                item['priority'] = m.group(1).decode()
                item['anpa_category'] = [{'qcode': m.group(2).decode()}]
                item['word_count'] = int(m.group(10).decode())
                if m.group(4) == b'\x12':
                    item['type'] = 'preformatted'

            # parse created date at the end of file
            m = re.search(b'\x03([a-z]+)-([a-z]+)-([0-9]+-[0-9]+-[0-9]+ [0-9]{2}[0-9]{2})GMT', lines[-4], flags=re.I)
            if m:
                item['firstcreated'] = datetime.strptime(m.group(3).decode(), '%m-%d-%y %H%M').replace(tzinfo=utc)

            # parse anpa content
            body = b''.join(lines[2:])
            m = re.match(b'\x02(.*)\x03', body, flags=re.M + re.S)
            if m:
                text = m.group(1).decode().split('\n')

                # text
                body_lines = [l.strip() for l in text if l.startswith('\t')]
                item['body_text'] = '\n'.join(body_lines)

                # content metadata
                header_lines = [l.strip('^<= ') for l in text if l.startswith('^')]
                if len(header_lines) > 3:
                    item['headline'] = header_lines[1]
                    item['byline'] = header_lines[-2]

                # slugline
                if len(header_lines) > 1:
                    m = re.match('[A-Z]{2}-[A-Z]{2}--([a-z-0-9]+)', header_lines[0], flags=re.I)
                    if m:
                        item['slugline'] = m.group(1)

                # ednote
                for line in header_lines:
                    m = re.search("EDITOR'S NOTE _(.*)", line)
                    if m:
                        item['ednote'] = m.group(1).strip()

            return item
        except Exception as ex:
            raise ParserError.anpaParseFileError(filename, ex)
