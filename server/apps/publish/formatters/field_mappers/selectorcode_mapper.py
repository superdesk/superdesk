# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from apps.publish.formatters.field_mappers import FieldMapper
import superdesk


class SelectorcodeMapper(FieldMapper):

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

    def map(self, article, subscriber, category, formatted_item):
        handlers = {
            'NATIONAL': self._set_ndx_selector_codes,
            'SPORTS': self._set_sdx_selector_codes,
            'FINANCE': self._set_fdx_selector_codes,
        }

        desk_id = article.get('task', {}).get('desk', None)
        if desk_id:
            desk = superdesk.get_resource_service('desks').find_one(req=None, _id=desk_id)
            handler = handlers.get(desk['name'].upper(), lambda *args: None)
            handler(article, subscriber['name'], formatted_item, category)

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
        if category == 'A' and article['urgency'] > 3:
            odbc_item['selector_codes'] = self.SELECTOR_CODES['newsd'][subscriber_name]
            return
        if category == 'A' and article['urgency'] <= 3:
            odbc_item['selector_codes'] = self._join_selector_codes(subscriber_name, 'newsd', 'cnewsd')
            return
        if category == 'I' and article['source'] == 'AAP':
            odbc_item['selector_codes'] = self._join_selector_codes(subscriber_name, 'newsd', 'cnewsd')
            return
        if category == 'I' and article['source'] != 'AAP' and article['urgency'] <= 3:
            odbc_item['selector_codes'] = self._join_selector_codes(subscriber_name, 'newsi', 'cnewsi')
            return
        if category == 'I' and article['source'] != 'AAP' and article['urgency'] > 3:
            odbc_item['selector_codes'] = self.SELECTOR_CODES['newsi'][subscriber_name]
            return
        if category == 'F' and article['source'] != 'AAP':
            odbc_item['selector_codes'] = self._join_selector_codes(subscriber_name,
                                                                    'financei', 'cfinancei', 'sfinancei', 'cnewsi')
            return
        if category == 'F' and article['source'] == 'AAP':
            odbc_item['selector_codes'] = self._join_selector_codes(subscriber_name, 'newsd', 'cnewsd')
            return
        if category == 'E' and article['source'] == 'AAP' \
                and article['urgency'] < 3 and self._is_in_subject(article, '010'):
            odbc_item['selector_codes'] = self._join_selector_codes(subscriber_name, 'eprem', 'newsd', 'cnewsd')
            return
        if category == 'E' and article['source'] != 'AAP' \
                and article['urgency'] < 3 and self._is_in_subject(article, '010'):
            odbc_item['selector_codes'] = self._join_selector_codes(subscriber_name, 'eprem', 'newsi', 'cnewsi')
            return
        if category == 'E' and article['urgency'] >= 3 and self._is_in_subject(article, '010'):
            odbc_item['selector_codes'] = self.SELECTOR_CODES['eprem'][subscriber_name]
            return
        if category == 'N' and article['source'] != 'NZN':
            odbc_item['selector_codes'] = self.SELECTOR_CODES['newsz'][subscriber_name]
            return

    def _set_sdx_selector_codes(self, article, subscriber_name, odbc_item, category):
        if 'NEWSLIST' in article['slugline'].upper():
            odbc_item['selector_codes'] = self._join_selector_codes(subscriber_name, 'sportmedia', 'sportseds')
            return
        if category == 'T' and article['source'] == 'AAP' and article['urgency'] > 3:
            odbc_item['selector_codes'] = self.SELECTOR_CODES['sportd'][subscriber_name]
            return
        if category == 'T' and article['source'] == 'AAP' and article['urgency'] <= 3:
            odbc_item['selector_codes'] = self._join_selector_codes(subscriber_name, 'sportd', 'csportd')
            return
        if category == 'S' and article['source'] == 'AAP':
            odbc_item['selector_codes'] = self._join_selector_codes(subscriber_name, 'sporti', 'csporti', 'csportd')
            return
        if category == 'S' and article['source'] != 'AAP' and article['urgency'] <= 3:
            odbc_item['selector_codes'] = self._join_selector_codes(subscriber_name, 'sporti', 'csporti')
            return
        if category == 'S' and article['source'] != 'AAP' and article['urgency'] > 3:
            odbc_item['selector_codes'] = self.SELECTOR_CODES['sporti'][subscriber_name]
            return

    def _set_fdx_selector_codes(self, article, subscriber_name, odbc_item, category):
        if category == 'F' and article['priority'] in ['N'] and article['urgency'] > 3:
            odbc_item['selector_codes'] = self.SELECTOR_CODES['sfinanced'][subscriber_name]
            return
        if category == 'F' and article['source'] == 'AAP' and article['priority'] in ['N', 'M']:
            odbc_item['selector_codes'] = self._join_selector_codes(subscriber_name,
                                                                    'financed', 'cfinanced', 'sfinanced')
            return
        if category == 'F' and article['source'] != 'AAP':
            odbc_item['selector_codes'] = self._join_selector_codes(subscriber_name,
                                                                    'financei', 'cfinancei', 'sfinancei')
            return
        if category == 'F' and article['source'] == 'AAP' \
                and article.get('locator', '') not in ['N', 'M']:
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
