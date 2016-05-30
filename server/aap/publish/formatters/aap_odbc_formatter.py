# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from superdesk.io.iptc import subject_codes
from apps.packages import TakesPackageService
from .aap_formatter_common import set_subject
from apps.archive.common import get_utc_schedule
from .field_mappers.locator_mapper import LocatorMapper
from superdesk.metadata.item import EMBARGO
import superdesk


class AAPODBCFormatter():

    def get_odbc_item(self, article, subscriber, category, codes):
        """
        Construct an odbc_item with the common key value pairs populated
        :param article:
        :param subscriber:
        :param category:
        :param codes:
        :return:
        """
        pub_seq_num = superdesk.get_resource_service('subscribers').generate_sequence_number(subscriber)
        odbc_item = dict(originator=article.get('source', None), sequence=pub_seq_num,
                         category=category.get('qcode'),
                         headline=article.get('headline', '').replace('\'', '\'\''),
                         author=article.get('byline', '').replace('\'', '\'\''),
                         keyword=self.append_legal(article=article, truncate=True).replace('\'', '\'\''),
                         subject_reference=set_subject(category, article),
                         take_key=article.get('anpa_take_key', '').replace('\'', '\'\''))
        if 'genre' in article and len(article['genre']) >= 1:
            odbc_item['genre'] = article['genre'][0].get('name', None)
        else:
            odbc_item['genre'] = 'Current'  # @genre
        odbc_item['news_item_type'] = 'News'
        odbc_item['fullStory'] = 1
        odbc_item['ident'] = '0'  # @ident
        odbc_item['selector_codes'] = ' '.join(codes) if codes else ' '

        headline_prefix = LocatorMapper().map(article, category.get('qcode').upper())
        if headline_prefix:
            odbc_item['headline'] = '{}:{}'.format(headline_prefix, odbc_item['headline'])

        self.expand_subject_codes(odbc_item)
        self.set_usn(odbc_item, article)

        return pub_seq_num, odbc_item

    def add_embargo(self, odbc_item, article):
        """
        Add the embargo text to the article if required
        :param odbc_item:
        :param article:
        :return:
        """
        if article.get(EMBARGO):
            embargo = '{}{}'.format('Embargo Content. Timestamp: ', get_utc_schedule(article, EMBARGO).isoformat())
            odbc_item['article_text'] = embargo + odbc_item['article_text']

    def expand_subject_codes(self, odbc_item):
        """
        Expands the subject reference to the subject matter and subject detail
        :param odbc_item:
        :return:
        """
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

    def set_usn(self, odbc_item, article):
        """
        Set the usn (unique story number) in the odbc item
        :param odbc_item:
        :param article:
        :return:
        """
        takes_package_service = TakesPackageService()
        pkg = takes_package_service.get_take_package(article)
        if pkg is not None:
            odbc_item['usn'] = pkg.get('unique_id', None)  # @usn
        else:
            odbc_item['usn'] = article.get('unique_id', None)  # @usn
