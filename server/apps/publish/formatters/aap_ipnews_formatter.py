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

from superdesk.publish.formatters import Formatter
from apps.publish.formatters.aap_formatter_common import map_priority, set_subject

import superdesk
from superdesk.errors import FormatterError
from superdesk.io.iptc import subject_codes
from apps.publish.formatters.field_mappers.selectorcode_mapper import SelectorcodeMapper
from apps.publish.formatters.field_mappers.locator_mapper import LocatorMapper
from superdesk.metadata.item import ITEM_TYPE, CONTENT_TYPE, EMBARGO


class AAPIpNewsFormatter(Formatter):

    def format(self, article, subscriber):
        """
        Constructs a dictionary that represents the parameters passed to the IPNews InsertNews stored procedure
        :return: returns the sequence number of the subscriber and the constructed parameter dictionary
        """
        try:
            docs = []
            for category in article.get('anpa_category'):
                pub_seq_num = superdesk.get_resource_service('subscribers').generate_sequence_number(subscriber)
                odbc_item = {'originator': article.get('source', None), 'sequence': pub_seq_num,
                             'category': category.get('qcode'),
                             'headline': article.get('headline', '').replace('\'', '\'\''),
                             'author': article.get('byline', '').replace('\'', '\'\''),
                             'keyword': article.get('slugline', None).replace('\'', '\'\''),
                             'subject_reference': set_subject(category, article)}

                if 'subject_reference' in odbc_item and odbc_item['subject_reference'] is not None \
                        and odbc_item['subject_reference'] != '00000000':
                    odbc_item['subject'] = subject_codes[odbc_item['subject_reference'][:2] + '000000']
                    if odbc_item['subject_reference'][2:5] != '000':
                        odbc_item['subject_matter'] = subject_codes[odbc_item['subject_reference'][:5] + '000']
                    else:
                        odbc_item['subject_matter'] = ''
                    if not odbc_item['subject_reference'].endswith('000'):
                        odbc_item['subject_detail'] = subject_codes[odbc_item['subject_reference']]
                    else:
                        odbc_item['subject_detail'] = ''
                else:
                    odbc_item['subject_reference'] = '00000000'

                odbc_item['take_key'] = article.get('anpa_take_key', None)  # @take_key
                odbc_item['usn'] = article.get('unique_id', None)  # @usn
                if article[ITEM_TYPE] == CONTENT_TYPE.PREFORMATTED:
                    odbc_item['article_text'] = article.get('body_html', '').replace('\'', '\'\'')  # @article_text
                elif article[ITEM_TYPE] == CONTENT_TYPE.TEXT:
                    soup = BeautifulSoup(article.get('body_html', ''))
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

                if 'genre' in article:
                    odbc_item['genre'] = article['genre'][0].get('name', None)
                else:
                    odbc_item['genre'] = 'Current'  # @genre
                if article.get(ITEM_TYPE, CONTENT_TYPE.TEXT) == CONTENT_TYPE.TEXT:
                    odbc_item['texttab'] = 'x'
                elif article.get(ITEM_TYPE, None) == CONTENT_TYPE.PREFORMATTED:
                    odbc_item['texttab'] = 't'
                odbc_item['wordcount'] = article.get('word_count', None)  # @wordcount
                odbc_item['news_item_type'] = 'News'
                odbc_item['priority'] = map_priority(article.get('priority'))  # @priority
                odbc_item['service_level'] = 'a'  # @service_level
                odbc_item['fullStory'] = 1
                odbc_item['ident'] = '0'  # @ident

                SelectorcodeMapper().map(article, category.get('qcode').upper(),
                                         subscriber=subscriber,
                                         formatted_item=odbc_item)
                headline_prefix = LocatorMapper().map(article, category.get('qcode').upper())
                if headline_prefix:
                    odbc_item['headline'] = '{}:{}'.format(headline_prefix, odbc_item['headline'])

                if article.get(EMBARGO):
                    embargo = '{}{}'.format('Embargo Content. Timestamp: ', article.get(EMBARGO).isoformat())
                    odbc_item['article_text'] = embargo + odbc_item['article_text']

                docs.append((pub_seq_num, odbc_item))

            return docs
        except Exception as ex:
            raise FormatterError.AAPIpNewsFormatterError(ex, subscriber)

    def can_format(self, format_type, article):
        return format_type == 'AAP IPNEWS' and article[ITEM_TYPE] in [CONTENT_TYPE.TEXT, CONTENT_TYPE.PREFORMATTED]
