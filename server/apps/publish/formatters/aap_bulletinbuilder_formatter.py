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
import superdesk
from superdesk.utils import json_serialize_datetime_objectId
from superdesk.errors import FormatterError
from bs4 import BeautifulSoup
from .field_mappers.locator_mapper import LocatorMapper


class AAPBulletinBuilderFormatter(Formatter):
    """
    Bulletin Builder Formatter
    """
    def format(self, article, subscriber):
        """
        Formats the article as require by the subscriber
        :param dict article: article to be formatted
        :param dict subscriber: subscriber receiving the article
        :return: tuple (int, str) of publish sequence of the subscriber, formatted article as string
        """
        try:
            pub_seq_num = superdesk.get_resource_service('subscribers').generate_sequence_number(subscriber)
            body_html = article.get('body_html', '').strip('\r\n')
            soup = BeautifulSoup(body_html)
            for br in soup.find_all('br'):
                # remove the <br> tag
                br.replace_with(' {}'.format(br.get_text()))

            for p in soup.find_all('p'):
                # replace <p> tag with two carriage return
                p.replace_with('{}\r\n\r\n'.format(p.get_text()))

            article['body_text'] = soup.get_text()

            # get the first category and derive the locator
            category = next((iter(article.get('anpa_category', []))), None)
            if category:
                locator = LocatorMapper().map(article, category.get('qcode').upper())
                if locator:
                    article['place'] = [{'qcode': locator, 'name': locator}]

            return [(pub_seq_num, superdesk.json.dumps(article, default=json_serialize_datetime_objectId))]
        except Exception as ex:
            raise FormatterError.bulletinBuilderFormatterError(ex, subscriber)

    def can_format(self, format_type, article):
        return format_type == 'AAP BULLETIN BUILDER'
