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
from superdesk.errors import FormatterError
from bs4 import BeautifulSoup
import datetime
from superdesk.metadata.item import ITEM_TYPE, CONTENT_TYPE, BYLINE, EMBARGO
from .field_mappers.selectorcode_mapper import SelectorcodeMapper
from .field_mappers.locator_mapper import LocatorMapper


class AAPAnpaFormatter(Formatter):
    def format(self, article, subscriber):
        try:
            docs = []
            for category in article.get('anpa_category'):
                pub_seq_num = superdesk.get_resource_service('subscribers').generate_sequence_number(subscriber)
                anpa = []

                # selector codes are only injected for those subscribers that are defined
                # in the mapper
                selectors = dict()
                SelectorcodeMapper().map(article, category.get('qcode').upper(),
                                         subscriber=subscriber,
                                         formatted_item=selectors)
                if 'selector_codes' in selectors and selectors['selector_codes']:
                    anpa.append(b'\x05')
                    anpa.append(selectors['selector_codes'].encode('ascii'))
                    anpa.append(b'\x0D\x0A')

                # start of message header (syn syn soh)
                anpa.append(b'\x16\x16\x01')
                anpa.append(article.get('service_level', 'a').lower().encode('ascii'))

                # story number
                anpa.append(str(pub_seq_num).zfill(4).encode('ascii'))

                # field seperator
                anpa.append(b'\x0A')  # -LF
                anpa.append(map_priority(article.get('priority')).encode('ascii'))
                anpa.append(b'\x20')

                anpa.append(category['qcode'].encode('ascii'))

                anpa.append(b'\x13')
                # format identifier
                if article[ITEM_TYPE] == CONTENT_TYPE.PREFORMATTED:
                    anpa.append(b'\x12')
                else:
                    anpa.append(b'\x11')
                anpa.append(b'\x20')

                # keyword
                keyword = 'bc-{}'.format(article.get('slugline', '')).replace(' ', '-')
                keyword = keyword[:24] if len(keyword) > 24 else keyword
                anpa.append(keyword.encode('ascii'))
                anpa.append(b'\x20')

                # version field
                anpa.append(b'\x20')

                # reference field
                anpa.append(b'\x20')

                # filing date
                anpa.append('{}-{}'.format(article['_updated'].strftime('%m'),
                                           article['_updated'].strftime('%d')).encode('ascii'))
                anpa.append(b'\x20')

                # add the word count
                anpa.append(str(article.get('word_count', '0000')).zfill(4).encode('ascii'))
                anpa.append(b'\x0D\x0A')

                anpa.append(b'\x02')  # STX

                self._process_headline(anpa, article, category['qcode'].encode('ascii'))

                keyword = article.get('slugline', '').encode('ascii', 'ignore')
                anpa.append(keyword)
                take_key = article.get('anpa_take_key', '').encode('ascii', 'ignore')
                anpa.append((b'\x20' + take_key) if len(take_key) > 0 else b'')
                anpa.append(b'\x0D\x0A')

                if BYLINE in article:
                    anpa.append(article.get(BYLINE).encode('ascii', 'ignore'))
                    anpa.append(b'\x0D\x0A')

                if 'dateline' in article and 'text' in article['dateline']:
                    anpa.append(article.get('dateline').get('text').encode('ascii', 'ignore'))

                if article.get(EMBARGO):
                    embargo = '{}{}'.format('Embargo Content. Timestamp: ', article.get(EMBARGO).isoformat())
                    article['body_html'] = embargo + article['body_html']

                if article[ITEM_TYPE] == CONTENT_TYPE.PREFORMATTED:
                    anpa.append(article.get('body_html', '').encode('ascii', 'replace'))
                else:
                    anpa.append(BeautifulSoup(article.get('body_html', '')).text.encode('ascii', 'replace'))

                anpa.append(b'\x0D\x0A')
                if article.get('more_coming', False):
                    anpa.append('MORE'.encode('ascii'))
                else:
                    anpa.append(article.get('source', '').encode('ascii'))
                sign_off = article.get('sign_off', '').encode('ascii')
                anpa.append((b'\x20' + sign_off) if len(sign_off) > 0 else b'')
                anpa.append(b'\x0D\x0A')

                anpa.append(b'\x03')  # ETX

                # time and date
                anpa.append(datetime.datetime.now().strftime('%d-%m-%y %H-%M-%S').encode('ascii'))

                anpa.append(b'\x04')  # EOT
                anpa.append(b'\x0D\x0A\x0D\x0A\x0D\x0A\x0D\x0A\x0D\x0A\x0D\x0A\x0D\x0A\x0D\x0A')

                docs.append((pub_seq_num, b''.join(anpa)))

            return docs
        except Exception as ex:
            raise FormatterError.AnpaFormatterError(ex, subscriber)

    def _process_headline(self, anpa, article, category):
        # prepend the locator to the headline if required
        headline_prefix = LocatorMapper().map(article, category.upper())
        if headline_prefix:
            headline = '{}:{}'.format(headline_prefix, article['headline'])
        else:
            headline = article.get('headline', '')

        # Set the maximum size to 64 including the sequence number if any
        if len(headline) > 64:
            if article.get('sequence'):
                digits = len(str(article['sequence'])) + 1
                shortened_headline = '{}={}'.format(headline[:-digits][:(64 - digits)], article['sequence'])
                anpa.append(shortened_headline.encode('ascii', 'replace'))
            else:
                anpa.append(headline[:64].encode('ascii', 'replace'))
        else:
            anpa.append(headline.encode('ascii', 'replace'))
        anpa.append(b'\x0D\x0A')

    def can_format(self, format_type, article):
        return format_type == 'AAP ANPA' and article[ITEM_TYPE] in [CONTENT_TYPE.TEXT, CONTENT_TYPE.PREFORMATTED]
