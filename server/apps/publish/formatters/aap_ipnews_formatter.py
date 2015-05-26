# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


from apps.publish.formatters import Formatter
import superdesk
from superdesk.errors import FormatterError
from bs4 import BeautifulSoup
from superdesk.io.iptc import subject_codes


class AAPIpNewsFormatter(Formatter):
    def format(self, article, output_channel, selector_codes):
        """ Constructs a dictionary that represents the parameters passed to the IPNews InsertNews stored procedure

        :param article:
        :param output_channel:
        :param selector_codes:
        :return: returns the sequence number of the output channel and the constructed parameter dictionary
        """
        try:

            pub_seq_num = superdesk.get_resource_service('output_channels').generate_sequence_number(output_channel)

            odbc_item = {}
            odbc_item['originator'] = article.get('originator', None)
            odbc_item['sequence'] = pub_seq_num
            odbc_item['category'] = article.get('anpa-category', {}).get('qcode')  # @category
            odbc_item['headline'] = article.get('headline', '')  # @headline
            odbc_item['author'] = article.get('byline', '')  # @author
            odbc_item['keyword'] = article.get('slugline', None)

            if article['subject'][0]:
                odbc_item['subject_reference'] = article['subject'][0].get('qcode', None)
                if odbc_item['subject_reference']:
                    odbc_item['subject'] = subject_codes[odbc_item['subject_reference'][:2] + '000000']
                    odbc_item['subject_matter'] = subject_codes[odbc_item['subject_reference'][:5] + '000']
                    odbc_item['subject_detail'] = subject_codes[odbc_item['subject_reference']]

            odbc_item['take_key'] = article.get('anpa_take_key', None)  # @take_key
            odbc_item['usn'] = article.get('unique_id', None)  # @usn
            if article['type'] == 'preformatted':
                odbc_item['article_text'] = article.get('body_html', '').replace('\'', '\'\'')  # @article_text
            elif article['type'] == 'text':
                text = BeautifulSoup(article.get('body_html', '')).text
                text = text.replace('\'', '\'\'')
                odbc_item['article_text'] = text

            if 'genre' in article:
                odbc_item['genre'] = article['genre'][0].get('name', None)
            else:
                odbc_item['genre'] = 'Current'  # @genre
            if article.get('type', 'text') == 'text':
                odbc_item['texttab'] = 'x'
            elif article.get('type', None) == 'preformatted':
                odbc_item['texttab'] = 't'
            odbc_item['wordcount'] = article.get('word_count', None)  # @wordcount
            odbc_item['news_item_type'] = 'News'
            odbc_item['priority'] = article.get('priority', None)  # @priority
            odbc_item['service_level'] = 'a'  # @service_level

            sel_codes = selector_codes[output_channel['_id']]
            odbc_item['selector_codes'] = ' '.join(sel_codes)

            odbc_item['fullStory'] = 1
            odbc_item['ident'] = '0'  # @ident

            return pub_seq_num, odbc_item
        except Exception as ex:
            raise FormatterError.AAPIpNewsFormatterError(ex, output_channel)

    def can_format(self, format_type, article_type):
        return format_type == 'AAP IPNEWS' and article_type in ['text', 'preformatted']
