# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


import textwrap
from io import StringIO
from bs4 import BeautifulSoup
from .aap_odbc_formatter import AAPODBCFormatter
from .aap_formatter_common import map_priority
from superdesk.publish.formatters import Formatter
from superdesk.errors import FormatterError
from superdesk.metadata.item import ITEM_TYPE, CONTENT_TYPE, FORMAT, FORMATS

import json


class AAPIpNewsFormatter(Formatter, AAPODBCFormatter):

    def format(self, article, subscriber, codes=None):
        """
        Constructs a dictionary that represents the parameters passed to the IPNews InsertNews stored procedure
        :return: returns the sequence number of the subscriber and the constructed parameter dictionary
        """
        try:
            docs = []
            for category in article.get('anpa_category'):
                pub_seq_num, odbc_item = self.get_odbc_item(article, subscriber, category, codes)

                soup = BeautifulSoup(self.append_body_footer(article), "html.parser")
                if article.get(FORMAT) == FORMATS.PRESERVED:  # @article_text
                    odbc_item['article_text'] = soup.get_text().replace('\'', '\'\'')
                    odbc_item['texttab'] = 't'
                elif article.get(FORMAT, FORMATS.HTML) == FORMATS.HTML:
                    text = StringIO()
                    for p in soup.findAll('p'):
                        text.write('\x19\r\n')
                        ptext = p.get_text('\n')
                        for l in ptext.split('\n'):
                            if len(l) > 80:
                                text.write(textwrap.fill(l, 80).replace('\n', ' \r\n'))
                            else:
                                text.write(l + ' \r\n')
                    odbc_item['article_text'] = text.getvalue().replace('\'', '\'\'')
                    odbc_item['texttab'] = 'x'

                self.add_embargo(odbc_item, article)

                odbc_item['service_level'] = 'a'  # @service_level
                odbc_item['wordcount'] = article.get('word_count', None)  # @wordcount
                odbc_item['priority'] = map_priority(article.get('priority'))  # @priority

                # Ta 20/04/16: Keeping selector code mapper section here for the time being
                # SelectorcodeMapper().map(article, category.get('qcode').upper(),
                #                          subscriber=subscriber,
                #                          formatted_item=odbc_item)

                docs.append((pub_seq_num, json.dumps(odbc_item)))

            return docs
        except Exception as ex:
            raise FormatterError.AAPIpNewsFormatterError(ex, subscriber)

    def can_format(self, format_type, article):
        return format_type == 'AAP IPNEWS' and article[ITEM_TYPE] in [CONTENT_TYPE.TEXT, CONTENT_TYPE.PREFORMATTED]
