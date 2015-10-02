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
from apps.publish.formatters.aap_formatter_common import map_priority
import superdesk
from bs4 import BeautifulSoup
from superdesk.errors import FormatterError
from superdesk.metadata.item import ITEM_TYPE, CONTENT_TYPE, EMBARGO


class AAPSMSFormatter(Formatter):
    def format(self, article, subscriber):
        """
        Constructs a dictionary that represents the parameters passed to the SMS InsertAlerts stored procedure
        :return: returns the sequence number of the subscriber and the constructed parameter dictionary
        """
        try:
            pub_seq_num = superdesk.get_resource_service('subscribers').generate_sequence_number(subscriber)

            odbc_item = {'Sequence': pub_seq_num, 'Category': article.get('anpa_category', [{}])[0].get('qcode'),
                         'Headline': article.get('headline', '').replace('\'', '\'\''),
                         'Priority': map_priority(article.get('priority'))}

            if article.get(EMBARGO):
                embargo = '{}{}'.format('Embargo Content. Timestamp: ', article.get(EMBARGO).isoformat())
                article['body_html'] = embargo + article['body_html']

            if article[ITEM_TYPE] == CONTENT_TYPE.PREFORMATTED:
                odbc_item['StoryText'] = article.get('body_html', '').replace('\'', '\'\'')  # @article_text
            elif article[ITEM_TYPE] == CONTENT_TYPE.TEXT:
                soup = BeautifulSoup(article.get('body_html', ''))
                odbc_item['StoryText'] = soup.text.replace('\'', '\'\'')

            odbc_item['ident'] = '0'

            return [(pub_seq_num, odbc_item)]
        except Exception as ex:
            raise FormatterError.AAPSMSFormatterError(ex, subscriber)

    def can_format(self, format_type, article):
        # need to check that a story with the same headline has not been published to SMS before
        lookup = {'destination.format': format_type, 'headline': article['headline']}
        published = superdesk.get_resource_service('publish_queue').get(req=None, lookup=lookup)
        if published and published.count():
            return False
        return format_type == 'AAP SMS' and article[ITEM_TYPE] in [CONTENT_TYPE.TEXT, CONTENT_TYPE.PREFORMATTED]
