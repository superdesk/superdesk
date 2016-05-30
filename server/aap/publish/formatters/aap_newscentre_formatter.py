# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


from superdesk.publish.formatters import Formatter
from bs4 import BeautifulSoup
from superdesk.errors import FormatterError
from superdesk.metadata.item import ITEM_TYPE, CONTENT_TYPE, FORMAT, FORMATS
from .aap_odbc_formatter import AAPODBCFormatter
from io import StringIO
import json


class AAPNewscentreFormatter(Formatter, AAPODBCFormatter):
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
                else:
                    text = StringIO()
                    for p in soup.findAll('p'):
                        text.write('   \r\n')
                        ptext = p.get_text('\n')
                        for l in ptext.split('\n'):
                            text.write(l + ' \r\n')
                    odbc_item['article_text'] = text.getvalue().replace('\'', '\'\'')

                self.add_embargo(odbc_item, article)

                odbc_item['category'] = odbc_item.get('category', '').upper()
                odbc_item['selector_codes'] = odbc_item.get('selector_codes', '').upper()

                docs.append((pub_seq_num, json.dumps(odbc_item)))

            return docs
        except Exception as ex:
            raise FormatterError.AAPNewscentreFormatterError(ex, subscriber)

    def can_format(self, format_type, article):
        return format_type == 'AAP NEWSCENTRE' and article[ITEM_TYPE] in [CONTENT_TYPE.TEXT, CONTENT_TYPE.PREFORMATTED]
