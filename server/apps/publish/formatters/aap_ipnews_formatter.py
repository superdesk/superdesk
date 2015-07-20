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

from apps.publish.formatters import Formatter
import superdesk
from superdesk.errors import FormatterError
from superdesk.io.iptc import subject_codes


class AAPIpNewsFormatter(Formatter):
    SELECTOR_CODES = {'monitor': {'newscentre': 'and bnd bxd bxx rnd rxd rxx',
                                  'ipnews': '0ah 0fh 0hw 0nl 0px bnd bxd bxx pnd pxd pxx rnd rxd rxx',
                                  'notes': 'bnd bxd bxx rnd rxd rxx'},
                      'newsi': {'newscentre': 'ani axi axx pni pxi pxx',
                                'ipnews': '0ah 0fh 0nl ani axi axx pni pxi pxx',
                                'notes': 'ani axi axx pni pxi pxx'},
                      'rnewsd': {'newscentre': 'and bnd bxd bxx rnd rxd rxx',
                                 'ipnews': '0fh bnd bxd bxx rnd rxd rxx',
                                 'notes': 'bnd bxd bxx rnd rxd rxx'},
                      'sportd': {'newscentre': 'asd axd axx psd pxd pxx',
                                 'ipnews': '0ah 0fh 0hw 0nl 0px 3ff 3nz 3pn 3rk asd axd axx psd pxd pxx',
                                 'notes': 'asd axd axx psd pxd pxx'},
                      'sfinancei': {'newscentre': 'afi afx axx pfi pfx pxx sfi sfx sxx',
                                    'ipnews': '0ah 0fh 0fr 0nl sfi sfx sxx',
                                    'notes': 'afi afx axx pfi pfx pxx sfi sfx sxx'},
                      'printsubs': {'newscentre': 'aax pad pai pax',
                                    'ipnews': '0ah 0fh 0hw 0nl 0px 0qn aax pad pai pax',
                                    'notes': 'aax pad pai pax'},
                      'cnewsi': {'newscentre': 'cni cxi cxx',
                                 'ipnews': 'cni cxi cxx',
                                 'notes': 'cni cxi cxx'},
                      'csportd': {'newscentre': 'csd cxd cxx',
                                  'ipnews': 'csd cxd cxx',
                                  'notes': 'csd cxd cxx'},
                      'sfinanced': {'newscentre': '2i1 2in 2mr afd sfd sfx sxx',
                                    'ipnews': '0ah 0fh 0fr 0hw 0nl 2in 2mr i1 in mr sfd sfx sxx',
                                    'notes': '2i1 2in 2mr sfd sfx sxx'},
                      'csporti': {'newscentre': 'csi cxi cxx',
                                  'ipnews': 'csi cxi cxx',
                                  'notes': 'csi cxi cxx'},
                      'cnewsd': {'newscentre': 'cnd cxd cxx',
                                 'ipnews': 'cnd cxd cxx',
                                 'notes': 'cnd cxd cxx'},
                      'fronters': {'newscentre': 'and axd axx bnd bxd bxx pnd pxd pxx rnd rxd rxx',
                                   'ipnews': '0ah 0fh 0hw 0ir 0nl 0px 0qn 3ff 3nz 3pn 3rk and axd axx '
                                             'az bnd bxd bxx pnd pxd pxx rnd rxd rxx',
                                   'notes': 'and axd axx bnd bxd bxx pnd pxd pxx rnd rxd rxx'},
                      'financei': {'newscentre': '2in afi axi axx pfi pxi pxx',
                                   'ipnews': '0ah 0fh 0nl 2in afi axi axx pfi pxi pxx',
                                   'notes': '2in afi axi axx pfi pxi pxx'},
                      'sporti': {'newscentre': 'asi axi axx psi pxi pxx',
                                 'ipnews': '0ah 0fh 0hw 0nl asi axi axx psi pxi pxx',
                                 'notes': 'asi axi axx psi pxi pxx'},
                      'cfinancei': {'newscentre': 'cfi cxi cxx',
                                    'ipnews': 'cfi cxi cxx',
                                    'notes': 'cfi cxi cxx'},
                      'newsd': {'newscentre': 'and axd axx pnd pxd pxx',
                                'ipnews': '0ah 0fh 0hw 0ir 0nl 0px and axd axx az pnd pxd pxx',
                                'notes': 'and axd axx pnd pxd pxx'},
                      'eprem': {'newscentre': 'jxx',
                                'ipnews': '0ah 0al 0fh 0hw 0nh 0nl 0pb 0px 0tb 0tc 0tn 0wm 3ff 3pn jxx'},
                      'newsnz': {'newscentre': 'nxx', 'notes': 'nxx', 'ipnews': 'nxx'}}

    def _set_subject(self, category, article):
        """
        Sets the subject code in the odbc_item based on the category, if multiple subject codes are available
        :param category:
        :param article:
        :return:
        """
        subject_reference = '        '
        # Ensure that there is a subject in the article
        if 'subject' in article and 'qcode' in article['subject'][0]:
            # set the subject reference with the first value, in case we can't do better
            subject_reference = article['subject'][0].get('qcode')
            # we have multiple categories and multiple subjects
            if len(article['subject']) > 1 and len(article['anpa_category']) > 1:
                # we need to find a more relevant subject reference if possible
                all_categories = superdesk.get_resource_service('vocabularies').find_one(req=None, _id='categories')
                ref_cat = [cat for cat in all_categories['items'] if
                           cat['qcode'].upper() == category['qcode'].upper()]
                # check if there is an associated subject with the category
                if ref_cat and len(ref_cat) == 1 and 'subject' in ref_cat[0]:
                    # try to find the lowest level subject that matches
                    ref = 0
                    for s in article['subject']:
                        if s['qcode'][:2] == ref_cat[0]['subject'][:2]:
                            if int(s['qcode']) > ref:
                                ref = int(s['qcode'])
                    if ref > 0:
                        subject_reference = '{0:0>8}'.format(ref)
        return subject_reference

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
                             'keyword': article.get('slugline', None).replace('\'', '\'\'')}

                odbc_item['subject_reference'] = self._set_subject(category, article)
                if 'subject_reference' in odbc_item:
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
                    odbc_item['subject_reference'] = '        '

                odbc_item['take_key'] = article.get('anpa_take_key', None)  # @take_key
                odbc_item['usn'] = article.get('unique_id', None)  # @usn
                if article['type'] == 'preformatted':
                    odbc_item['article_text'] = article.get('body_html', '').replace('\'', '\'\'')  # @article_text
                elif article['type'] == 'text':
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
                if article.get('type', 'text') == 'text':
                    odbc_item['texttab'] = 'x'
                elif article.get('type', None) == 'preformatted':
                    odbc_item['texttab'] = 't'
                odbc_item['wordcount'] = article.get('word_count', None)  # @wordcount
                odbc_item['news_item_type'] = 'News'
                odbc_item['priority'] = article.get('priority', 'r')  # @priority
                odbc_item['service_level'] = 'a'  # @service_level
                odbc_item['fullStory'] = 1
                odbc_item['ident'] = '0'  # @ident

                self._set_selector_codes(article, subscriber['name'], odbc_item, category)
                docs.append((pub_seq_num, odbc_item))

            return docs
        except Exception as ex:
            raise FormatterError.AAPIpNewsFormatterError(ex, subscriber)

    def can_format(self, format_type, article):
        return format_type == 'AAP IPNEWS' and article['type'] in ['text', 'preformatted']

    def _set_selector_codes(self, article, subscriber_name, odbc_item, category):
        handlers = {
            'NATIONAL': self._set_ndx_selector_codes,
            'SPORTS': self._set_sdx_selector_codes,
            'FINANCE': self._set_fdx_selector_codes,
        }

        desk_id = article.get('task', {}).get('desk', None)
        if desk_id:
            desk = superdesk.get_resource_service('desks').find_one(req=None, _id=desk_id)
            handler = handlers.get(desk['name'].upper(), lambda *args: None)
            handler(article, subscriber_name, odbc_item, category)

    def _set_ndx_selector_codes(self, article, subscriber_name, odbc_item, category):
        slugline = article['slugline'].upper()

        if 'MONITOR' in slugline:
            odbc_item['selector_codes'] = self.SELECTOR_CODES['monitor'][subscriber_name]
            return
        if 'DIARY' in slugline:
            odbc_item['selector_codes'] = self._join_selector_codes(subscriber_name, 'printsubs', 'cnewsd', 'rnewsd')
            return
        if 'FRONTERS' in slugline:
            odbc_item['selector_codes'] = self.SELECTOR_CODES['fronters'][subscriber_name]
            return
        if category['qcode'] == 'A' and article['urgency'] > 3:
            odbc_item['selector_codes'] = self.SELECTOR_CODES['newsd'][subscriber_name]
            return
        if category['qcode'] == 'A' and article['urgency'] <= 3:
            odbc_item['selector_codes'] = self._join_selector_codes(subscriber_name, 'newsd', 'cnewsd')
            return
        if category['qcode'] == 'I' and article['source'] == 'AAP':
            odbc_item['selector_codes'] = self._join_selector_codes(subscriber_name, 'newsd', 'cnewsd')
            return
        if category['qcode'] == 'I' and article['source'] != 'AAP' and article['urgency'] <= 3:
            odbc_item['selector_codes'] = self._join_selector_codes(subscriber_name, 'newsi', 'cnewsi')
            return
        if category['qcode'] == 'I' and article['source'] != 'AAP' and article['urgency'] > 3:
            odbc_item['selector_codes'] = self.SELECTOR_CODES['newsi'][subscriber_name]
            return
        if category['qcode'] == 'F' and article['source'] != 'AAP':
            odbc_item['selector_codes'] = self._join_selector_codes(subscriber_name,
                                                                    'financei', 'cfinancei', 'sfinancei', 'cnewsi')
            return
        if category['qcode'] == 'F' and article['source'] != 'AAP':
            odbc_item['selector_codes'] = self._join_selector_codes(subscriber_name, 'newsd', 'cnewsd')
            return
        if category['qcode'] == 'E' and article['source'] == 'AAP' \
                and article['urgency'] < 3 and self._is_in_subject('010'):
            odbc_item['selector_codes'] = self._join_selector_codes(subscriber_name, 'eprem', 'newsd', 'cnewsd')
            return
        if category['qcode'] == 'E' and article['source'] != 'AAP' \
                and article['urgency'] < 3 and self._is_in_subject('010'):
            odbc_item['selector_codes'] = self._join_selector_codes(subscriber_name, 'eprem', 'newsi', 'cnewsi')
            return
        if category['qcode'] == 'E' and article['urgency'] >= 3 and self._is_in_subject('010'):
            odbc_item['selector_codes'] = self.SELECTOR_CODES['eprem'][subscriber_name]
            return
        if category['qcode'] == 'N' and article['source'] != 'NZN':
            odbc_item['selector_codes'] = self.SELECTOR_CODES['newsz'][subscriber_name]
            return

    def _set_sdx_selector_codes(self, article, subscriber_name, odbc_item, category):
        if 'NEWSLIST' in article['slugline'].upper():
            odbc_item['selector_codes'] = self._join_selector_codes(subscriber_name, 'sportmedia', 'sportseds')
            return
        if category['qcode'] == 'T' and article['source'] == 'AAP' and article['urgency'] > 3:
            odbc_item['selector_codes'] = self.SELECTOR_CODES['sportd'][subscriber_name]
            return
        if category['qcode'] == 'T' and article['source'] == 'AAP' and article['urgency'] <= 3:
            odbc_item['selector_codes'] = self._join_selector_codes(subscriber_name, 'sportd', 'csportd')
            return
        if category['qcode'] == 'S' and article['source'] == 'AAP':
            odbc_item['selector_codes'] = self._join_selector_codes(subscriber_name, 'sporti', 'csporti', 'csportd')
            return
        if category['qcode'] == 'S' and article['source'] != 'AAP' and article['urgency'] <= 3:
            odbc_item['selector_codes'] = self._join_selector_codes(subscriber_name, 'sporti', 'csporti')
            return
        if category['qcode'] == 'S' and article['source'] != 'AAP' and article['urgency'] > 3:
            odbc_item['selector_codes'] = self.SELECTOR_CODES['sporti'][subscriber_name]
            return

    def _set_fdx_selector_codes(self, article, subscriber_name, odbc_item, category):
        if category['qcode'] == 'F' and article['priority'] in ['N'] and article['urgency'] > 3:
            odbc_item['selector_codes'] = self.SELECTOR_CODES['sfinanced'][subscriber_name]
            return
        if category['qcode'] == 'F' and article['source'] == 'AAP' and article['priority'] in ['N', 'M']:
            odbc_item['selector_codes'] = self._join_selector_codes(subscriber_name,
                                                                    'financed', 'cfinanced', 'sfinanced')
            return
        if category['qcode'] == 'F' and article['source'] != 'AAP':
            odbc_item['selector_codes'] = self._join_selector_codes(subscriber_name,
                                                                    'financei', 'cfinancei', 'sfinancei')
            return
        if category['qcode'] == 'F' and article['source'] == 'AAP' and article.get('locator', '') not in ['N', 'M']:
            odbc_item['selector_codes'] = self._join_selector_codes(subscriber_name,
                                                                    'financei', 'cfinancei', 'sfinancei')
            return

    def _join_selector_codes(self, subscriber_name, *args):
        codes = []
        for arg in args:
            codes.extend(self.SELECTOR_CODES[arg][subscriber_name.lower()].split())
        return ' '.join(list(set(codes)))

    def _is_in_subject(self, article, qcode):
        def compare(code1, code2):
            return code1[:len(code2)] == code2

        return any(compare(s['qcode'], qcode) for s in article.get('subject', []))
