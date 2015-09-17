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
import logging

logger = logging.getLogger(__name__)


class SelectorcodeMapper(FieldMapper):
    SELECTOR_CODES = {'sportdmedia': {'ipnews': '0ah 0fh 0hw 0nl 0px psd pxd pxx'},
                      'rnewsdnt': {'ipnews': '0fh bn8 bx8 rn8 rx8'},
                      'newsnz': {'newscentre': 'nxx', 'ipnews': 'nxx', 'notes': 'nxx'},
                      'newsdnotqld': {'ipnews': '0ah 0fh 0hw 0nl 0px an2 an3 an5 an6 an7 an8 ax2 ax3 ax5 ax6 ax7 ax8 '
                                      + 'pn2 pn3 pn5 pn6 pn7 px0 px2 px3 px5 px6 px7 px8'},
                      'rnewsdnotnsw': {
                          'ipnews': 'bn3 bn4 bn5 bn6 bn7 bx3 bx4 bx5 bx6 bx7 bx8 rn3 rn4 rn5 rn6 rn7 rx3 rx4 rx5 rx6 '
                          'rx7 rx8'},
                      'rnewsdnotwa': {
                          'ipnews': '0fh bn2 bn3 bn4 bn5 bn7 bx2 bx3 bx4 bx5 bx7 bx8 rn2 rn3 rn4 rn5 rn7 rx2 rx3 rx4 '
                          + 'rx5 rx7 rx8'},
                      'sportdsa': {'ipnews': '0ah 0fh 0nl 3ff 3nz 3pn 3rk as5 ax5 ps5 px5'},
                      'newsd': {'newscentre': 'and axd axx pnd pxd pxx',
                                'ipnews': '0ah 0fh 0hw 0ir 0nl 0px and axd axx az pnd pxd pxx',
                                'notes': 'and axd axx pnd pxd pxx'},
                      'newsdvic': {'ipnews': '0fh 0hw 0ir an3 ax3 az pn3 px3'},
                      'rnewsdvic': {'ipnews': '0fh bn3 bx3 rn3 rx3'},
                      'newsdnottas': {
                          'ipnews': '0ah 0fh 0hw 0nl 0px an2 an3 an4 an5 an6 an8 ax2 ax3 ax4 ax5 ax6 ax8 pn2 pn3 pn4 '
                          + 'pn5 pn6 px0 px2 px3 px4 px5 px6 px8'},
                      'newsdnsw': {'ipnews': '0fh 0ir 0nl an2 ax2 az pn2 px2'},
                      'rnewsdnotsa': {
                          'ipnews': '0fh bn2 bn3 bn4 bn6 bn7 bx2 bx3 bx4 bx6 bx7 bx8 rn2 rn3 rn4 rn6 rn7 rx2 rx3 rx4 '
                          + 'rx6 rx7 rx8'},
                      'sfinancei': {'newscentre': 'afi afx axx pfi pfx pxx sfi sfx sxx',
                                    'ipnews': '0ah 0fh 0fr 0nl sfi sfx sxx',
                                    'notes': 'afi afx axx pfi pfx pxx sfi sfx sxx'},
                      'newsdwa': {'ipnews': '0ir 0px an6 ax6 az pn6 px6'},
                      'newsdnotnt': {
                          'ipnews': '0ah 0fh 0hw 0nl an2 an3 an4 an5 an6 an7 ax2 ax3 ax4 ax5 ax6 ax7 pn2 pn3 pn4 pn5 '
                          + 'pn6 pn7 px0 px2 px3 px4 px5 px6 px7'},
                      'newsi': {'newscentre': 'ani axi axx pni pxi pxx',
                                'ipnews': '0ah 0fh 0nl ani axi axx pni pxi pxx',
                                'notes': 'ani axi axx pni pxi pxx'},
                      'rnewsdtas': {'ipnews': '0fh bn7 bx7 rn7 rx7'},
                      'sporti': {'newscentre': 'asi axi axx psi pxi pxx',
                                 'ipnews': '0ah 0fh 0hw 0nl asi axi axx psi pxi pxx',
                                 'notes': 'asi axi axx psi pxi pxx'},
                      'sportdvic': {'ipnews': '0ab 0fh 0hw 0nl 3ff 3nz 3pn 3rk as3 ax3 ps3 px3'},
                      'sportdnsw': {'ipnews': '0fh 0nl 3ff 3nz 3pn 3rk as2 ax2 ps2 px2'},
                      'sportd': {'newscentre': 'asd axd axx psd pxd pxx',
                                 'ipnews': '0ah 0fh 0hw 0nl 0px 3ff 3nz 3pn 3rk asd axd axx psd pxd pxx',
                                 'notes': 'asd axd axx psd pxd pxx'},
                      'newsdsa': {'ipnews': '0ah 0ir an5 ax5 az pn5 px5'},
                      'monitor': {'newscentre': 'and bnd bxd bxx rnd rxd rxx',
                                  'ipnews': '0ah 0fh 0hw 0nl 0px bnd bxd bxx pnd pxd pxx rnd rxd rxx',
                                  'notes': 'bnd bxd bxx rnd rxd rxx'},
                      'csporti': {'newscentre': 'csi cxi cxx', 'ipnews': 'csi cxi cxx', 'notes': 'csi cxi cxx'},
                      'financei': {'newscentre': '2in afi axi axx pfi pxi pxx',
                                   'ipnews': '0ah 0fh 0nl 2in afi axi axx pfi pxi pxx',
                                   'notes': '2in afi axi axx pfi pxi pxx'},
                      'newsdqld': {'ipnews': '0ir an4 ax4 az pn4 px4'},
                      'cnewsi': {'newscentre': 'cni cxi cxx', 'ipnews': 'cni cxi cxx', 'notes': 'cni cxi cxx'},
                      'newsdnotnsw': {
                          'ipnews': '0ah 0fh 0hw 0px an3 an4 an5 an6 an7 an8 ax3 ax4 ax5 ax6 ax7 ax8 pn3 pn4 pn5 pn6 '
                          + 'pn7 px0 px3 px4 px5 px6 px7 px8'},
                      'rnewsd': {'newscentre': 'and bnd bxd bxx rnd rxd rxx', 'ipnews': '0fh bnd bxd bxx rnd rxd rxx',
                                 'notes': 'bnd bxd bxx rnd rxd rxx'},
                      'rnewsdnotnt': {
                          'ipnews': '0fh bn2 bn3 bn4 bn5 bn6 bn7 bx2 bx3 bx4 bx5 bx6 bx7 rn2 rn3 rn4 rn5 rn6 rn7 '
                          + 'rx2 rx3 rx4 rx5 rx6 rx7'},
                      'eprem': {'newscentre': 'jxx',
                                'ipnews': '0ah 0al 0fh 0hw 0nh 0nl 0pb 0px 0tb 0tc 0tn 0wm 3ff 3pn jxx'},
                      'newsdtas': {'ipnews': '0ir an7 ax7 az pn7 px7'},
                      'sfinanced': {'newscentre': '2i1 2in 2mr afd sfd sfx sxx',
                                    'ipnews': '0ah 0fh 0fr 0hw 0nl 2in 2mr i1 in mr sfd sfx sxx',
                                    'notes': '2i1 2in 2mr sfd sfx sxx'},
                      'csportd': {'newscentre': 'csd cxd cxx',
                                  'ipnews': 'csd cxd cxx',
                                  'notes': 'csd cxd cxx'},
                      'fronters': {'newscentre': 'and axd axx bnd bxd bxx pnd pxd pxx rnd rxd rxx',
                                   'ipnews': '0ah 0fh 0hw 0ir 0nl 0px 0qn 3ff 3nz 3pn 3rk and axd axx az bnd bxd '
                                   + 'bxx pnd pxd pxx rnd rxd rxx',
                                   'notes': 'and axd axx bnd bxd bxx pnd pxd pxx rnd rxd rxx'},
                      'rnewsdsa': {'ipnews': '0fh bn5 bx5 rn5 rx5'},
                      'sportdwa': {'ipnews': '0fh 0nl 0px 3ff 3nz 3pn 3rk as6 ax6 ps6 px6'},
                      'rnewsdnsw': {'ipnews': '0fh bn2 bx2 rn2 rx2'},
                      'rnewsdnottas': {
                          'ipnews': '0fh bn2 bn3 bn4 bn5 bn6 bx2 bx3 bx4 bx5 bx6 bx8 rn2 rn3 rn4 rn5 rn6 rx2 rx3 '
                          + 'rx4 rx5 rx6 rx8'},
                      'printsubs': {'newscentre': 'aax pad pai pax',
                                    'ipnews': '0ah 0fh 0hw 0nl 0px 0qn aax pad pai pax',
                                    'notes': 'aax pad pai pax'},
                      'sportdtas': {'ipnews': '0fh 0nl 3ff 3nz 3pn 3rk as7 ax7 ps7 px7'},
                      'cnewsd': {'newscentre': 'cnd cxd cxx',
                                 'ipnews': 'cnd cxd cxx',
                                 'notes': 'cnd cxd cxx'},
                      'newsdnotsa': {
                          'ipnews': '0fh 0hw 0nl 0px an2 an3 an4 an6 an7 an8 ax2 ax3 ax4 ax6 ax7 ax8 pn2 pn3 pn4 pn6 '
                          + 'pn7 px0 px2 px3 px4 px6 px7 px8'},
                      'rnewsdqld': {'ipnews': '0fh bn4 bx4 rn4 rx4'},
                      'newsdnotvic': {
                          'ipnews': '0ah 0fh 0nl 0px an2 an4 an5 an6 an7 an8 ax2 ax4 ax5 ax6 ax7 ax8 pn2 pn4 pn5 '
                          + 'pn6 pn7 px0 px2 px4 px5 px6 px7 px8'},
                      'newsdnotwa': {
                          'ipnews': '0ah 0fh 0hw 0nl an2 an3 an4 an5 an7 an8 ax2 ax3 ax4 ax5 ax7 ax8 pn2 pn3 pn4 pn5 '
                          + 'pn7 px0 px2 px3 px4 px5 px7 px8'},
                      'rnewsdnotqld': {
                          'ipnews': '0fh bn2 bn3 bn5 bn6 bn7 bx2 bx3 bx5 bx6 bx7 bx8 rn2 rn3 rn5 rn6 rn7 rx2 rx3 rx5 '
                          + 'rx6 rx7 rx8'},
                      'rnewsdwa': {'ipnews': '0fh bn6 bx6 rn6 rx6'},
                      'rnewsdnotvic': {
                          'ipnews': '0fh bn2 bn4 bn5 bn6 bn7 bx2 bx4 bx5 bx6 bx7 bx8 rn2 rn4 rn5 rn6 rn7 rx2 rx4 '
                          + 'rx5 rx6 rx7 rx8'},
                      'sportdqld': {'ipnews': '0fh 0nl 0qn 3ff 3nz 3pn 3rk as4 ax4 ps4 px4'},
                      'cfinancei': {'newscentre': 'cfi cxi cxx',
                                    'ipnews': 'cfi cxi cxx',
                                    'notes': 'cfi cxi cxx'}}

    def map(self, article, category, **kwargs):
        handlers = {
            'NATIONAL': self._set_ndx_selector_codes,
            'SPORT': self._set_sdx_selector_codes,
            'FINANCE': self._set_fdx_selector_codes,
        }

        desk_id = article.get('task', {}).get('desk', None)
        if desk_id:
            desk = superdesk.get_resource_service('desks').find_one(req=None, _id=desk_id)
            subscriber = kwargs['subscriber']
            formatted_item = kwargs['formatted_item']
            handler = handlers.get(desk['name'].upper(), lambda *args: None)
            handler(article, subscriber['name'], formatted_item, category)

    def _get_geo_abbreviation(self, name):
        """
        passed the name that is kept in the article uses it to find the value from the vocabulary
        :param name:
        :return: the abbreviatoin for the geographical restriction
        """
        geo_resource = superdesk.get_resource_service('vocabularies').find_one(req=None,
                                                                               _id='geographical_restrictions')
        item = next((i for i in geo_resource.get('items') if i['name'] == name), None)
        if item:
            return item.get('value')
        else:
            return ''

    def set_selectors_for_dg(self, article, subscriber_name, *dist_groups):
        """
        Test if there is a geo block, if there is calculate the required selector codes, if not just join as normal
        :param article:
        :param subscriber_name:
        :param dist_groups:
        :return: Space seperated string of selector codes
        """
        # if the is a geographical block
        if 'targeted_for' in article and len(article.get('targeted_for')) > 0:
            selector_set = set()
            # scan each block clause
            for geo_block in article.get('targeted_for'):
                # scan each distribution group
                for dg in dist_groups:
                    if geo_block.get('allow'):
                        geo_value = dg + self._get_geo_abbreviation(geo_block.get('name')).lower()
                        if geo_value in self.SELECTOR_CODES and subscriber_name.lower() in \
                                self.SELECTOR_CODES[geo_value]:
                            selector_set = selector_set | \
                                set(self.SELECTOR_CODES[geo_value][subscriber_name.lower()].split(' '))
                    else:
                        geo_value = dg + 'not' + self._get_geo_abbreviation(geo_block.get('name')).lower()
                        if geo_value in self.SELECTOR_CODES and subscriber_name.lower() in \
                                self.SELECTOR_CODES[geo_value]:
                            if selector_set:
                                selector_set = selector_set & \
                                    set(self.SELECTOR_CODES[geo_value][subscriber_name.lower()].split(' '))
                            else:
                                selector_set = set(self.SELECTOR_CODES[geo_value][subscriber_name.lower()].split(' '))
            return ' '.join((list(selector_set)))
        else:  # normal case just join the distribution groups
            return self._join_selector_codes(subscriber_name, *dist_groups)

    def _set_ndx_selector_codes(self, article, subscriber_name, odbc_item, category):
        slugline = article['slugline'].upper()

        if 'MONITOR' in slugline:
            odbc_item['selector_codes'] = self.set_selectors_for_dg(article, subscriber_name, 'monitor')
            return
        if 'DIARY' in slugline:
            odbc_item['selector_codes'] = self.set_selectors_for_dg(article, subscriber_name,
                                                                    'printsubs', 'cnewsd', 'rnewsd')
            return
        if 'FRONTERS' in slugline:
            odbc_item['selector_codes'] = self.set_selectors_for_dg(article, subscriber_name, 'fronters')
            return
        if category == 'A' and article['urgency'] > 3:
            odbc_item['selector_codes'] = self.set_selectors_for_dg(article, subscriber_name, 'newsd')
            return
        if category == 'A' and article['urgency'] <= 3:
            odbc_item['selector_codes'] = self.set_selectors_for_dg(article, subscriber_name, 'newsd', 'cnewsd')
            return
        if category == 'I' and article['source'] == 'AAP':
            odbc_item['selector_codes'] = self.set_selectors_for_dg(article, subscriber_name, 'newsd', 'cnewsd')
            return
        if category == 'I' and article['source'] != 'AAP' and article['urgency'] <= 3:
            odbc_item['selector_codes'] = self.set_selectors_for_dg(article, subscriber_name, 'newsi', 'cnewsi')
            return
        if category == 'I' and article['source'] != 'AAP' and article['urgency'] > 3:
            odbc_item['selector_codes'] = self.set_selectors_for_dg(article, subscriber_name, 'newsi')
            return
        if category == 'F' and article['source'] != 'AAP':
            odbc_item['selector_codes'] = self.set_selectors_for_dg(article, subscriber_name,
                                                                    'financei', 'cfinancei', 'sfinancei', 'cnewsi')
            return
        if category == 'F' and article['source'] == 'AAP':
            odbc_item['selector_codes'] = self.set_selectors_for_dg(article, subscriber_name, 'newsd', 'cnewsd')
            return
        if category == 'E' and article['source'] == 'AAP' \
                and article['urgency'] < 3 and self._is_in_subject(article, '010'):
            odbc_item['selector_codes'] = self.set_selectors_for_dg(article, subscriber_name,
                                                                    'eprem', 'newsd', 'cnewsd')
            return
        if category == 'E' and article['source'] != 'AAP' \
                and article['urgency'] < 3 and self._is_in_subject(article, '010'):
            odbc_item['selector_codes'] = self.set_selectors_for_dg(article, subscriber_name,
                                                                    'eprem', 'newsi', 'cnewsi')
            return
        if category == 'E' and article['urgency'] >= 3 and self._is_in_subject(article, '010'):
            odbc_item['selector_codes'] = self.set_selectors_for_dg(article, subscriber_name, 'eprem')
            return
        if category == 'N' and article['source'] != 'NZN':
            odbc_item['selector_codes'] = self.set_selectors_for_dg(article, subscriber_name, 'newsz')
            return
        odbc_item['selector_codes'] = '   '
        logger.error('No Selector code derived from National desk')

    def _set_sdx_selector_codes(self, article, subscriber_name, odbc_item, category):
        if 'NEWSLIST' in article['slugline'].upper():
            odbc_item['selector_codes'] = self.set_selectors_for_dg(article, subscriber_name, 'sportmedia', 'sportseds')
            return
        if category == 'T' and article['source'] == 'AAP' and article['urgency'] > 3:
            odbc_item['selector_codes'] = self.set_selectors_for_dg(article, subscriber_name, 'sportd')
            return
        if category == 'T' and article['source'] == 'AAP' and article['urgency'] <= 3:
            odbc_item['selector_codes'] = self.set_selectors_for_dg(article, subscriber_name, 'sportd', 'csportd')
            return
        if category == 'S' and article['source'] == 'AAP':
            odbc_item['selector_codes'] = self.set_selectors_for_dg(article, subscriber_name,
                                                                    'sporti', 'csporti', 'csportd')
            return
        if category == 'S' and article['source'] != 'AAP' and article['urgency'] <= 3:
            odbc_item['selector_codes'] = self.set_selectors_for_dg(article, subscriber_name, 'sporti', 'csporti')
            return
        if category == 'S' and article['source'] != 'AAP' and article['urgency'] > 3:
            odbc_item['selector_codes'] = self.set_selectors_for_dg(article, subscriber_name, 'sporti')
            return
        odbc_item['selector_codes'] = '   '
        logger.error('No Selector code derived from sport desk')

    def _set_fdx_selector_codes(self, article, subscriber_name, odbc_item, category):
        if category == 'F' and article['priority'] in ['N'] and article['urgency'] > 3:
            odbc_item['selector_codes'] = self.set_selectors_for_dg(article, subscriber_name, 'sfinanced')
            return
        if category == 'F' and article['source'] == 'AAP' and article['priority'] in ['N', 'M']:
            odbc_item['selector_codes'] = self.set_selectors_for_dg(article, subscriber_name,
                                                                    'financed', 'cfinanced', 'sfinanced')
            return
        if category == 'F' and article['source'] != 'AAP':
            odbc_item['selector_codes'] = self.set_selectors_for_dg(article, subscriber_name,
                                                                    'financei', 'cfinancei', 'sfinancei')
            return
        if category == 'F' and article['source'] == 'AAP' \
                and article.get('locator', '') not in ['N', 'M']:
            odbc_item['selector_codes'] = self.set_selectors_for_dg(article, subscriber_name,
                                                                    'financei', 'cfinancei', 'sfinancei')
            return
        odbc_item['selector_codes'] = '   '
        logger.error('No Selector code derived from Finance desk')

    def _join_selector_codes(self, subscriber_name, *args):
        codes = []
        for arg in args:
            if arg in self.SELECTOR_CODES and subscriber_name.lower() in self.SELECTOR_CODES[arg]:
                codes.extend(self.SELECTOR_CODES[arg][subscriber_name.lower()].split())
        return ' '.join(list(set(codes)))

    def _is_in_subject(self, article, qcode):
        def compare(code1, code2):
            return code1[:len(code2)] == code2

        return any(compare(s['qcode'], qcode) for s in article.get('subject', []))
