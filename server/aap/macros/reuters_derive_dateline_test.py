# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from unittest import TestCase
from .reuters_derive_dateline import reuters_derive_dateline
import datetime


class DPADeriveDatelineTests(TestCase):
    def simple_case_test(self):
        item = dict()
        item['firstcreated'] = datetime.datetime(2015, 10, 26, 11, 45, 19, 0)
        item['body_html'] = '<p>DETROIT (Reuters) - General Motors Co <GM.N> Chief Financial Officer Chuck Stevens \
            said on Wednesday the macroeconomic challenges in Brazil will remain in the near term but the company \
            has \"huge upside leverage once the macro situation changes\" in South America\'s largest \
            economy.</p>\n<p>GM\'s car sales so far in October are up versus a year ago, Stevens said to reporters \
            after the No. 1 U.S. automaker reported third-quarter financial results.</p>\n<p>Stevens also \
            reaffirmed GM\'s past forecasts that it will show profit in Europe in 2016. It would be GM\'s first \
            profit in Europe since 1999.</p>\n<p> (Reporting by Bernie Woodall and Joseph White; \
            Editing by Chizu Nomiyamam and Jeffrey Benkoe)</p>'
        reuters_derive_dateline(item)
        self.assertEqual(item['dateline']['located']['city'], 'Detroit')

    def with_a_date_test(self):
        item = dict()
        item['firstcreated'] = datetime.datetime(2015, 10, 26, 11, 45, 19, 0)
        item['body_html'] = '<p>PARIS, Oct 22 (Reuters) - Eurotunnel said on\nThursday that third-quarter revenue \
        rose 3 percent to 334.4\nmillion euros ($379.48 million), as economic recovery helped\noffset the \
        impact of the disruption to traffic resulting from\nthe migrant crisis.</p>\n<p>The operator of the \
        Channel Tunnel linking France and\nBritain said that business remained dynamic, driven by a\nrecovering \
        economy in Britain and to a lesser extent in the\neuro-zone.</p>\n<p>But a camp of around 6,000 migrants \
        in the Calais area\nfleeing war, political turmoil and poverty outside Europe has\ncaused disruption to \
        traffic since Summer.</p>\n<p>Eurotunnel carries Eurostar high-speed trains between Paris,\nBrussels and \
        London, as well as shuttle trains containing\npassenger cars, coaches and freight trucks.</p>\n<p>Rail \
        freight tonnage fell 27 percent year-on-year and the\nnumber of freight trains using the Channel \
        tunnel fell 33\npercent, the company said - blaming the drop on the migrant\ncrisis.</p>\n<p>Passenger \
        traffic in the quarter rose 2 percent year-on-year\nto 2,866,155 on the Eurostar. Traffic however fell \
        1 percent on\ntrucks and 9 percent on coaches compared with the same period\nlast year.</p>\n<p>In July \
        Eurotunnel asked the French and British governments\nto reimburse it for close to 10 million euros it spent \
        to beef\nup security to cope with a migrant crisis at the French port of\nCalais.</p>\n<p>Third quarter \
        sales figures no longer include MyFerryLink,\nthe ferry service between Britain and France, which ended \
        its \nits activity on June 29.</p>\n<p>($1 = 0.8812 euros)\n\n (Reporting by Dominique Vidalon; Editing \
        by Andrew Callus)</p>",'
        reuters_derive_dateline(item)
        self.assertEqual(item['dateline']['located']['city'], 'PARIS')

    def with_a_byline_test(self):
        item = dict()
        item['firstcreated'] = datetime.datetime(2015, 10, 26, 11, 45, 19, 0)
        item['byline'] = 'By Karl Plume'
        item['body_html'] = '<p>By Karl Plume</p>\n<p>CHICAGO, Oct 21 (Reuters) - Chicago Cubs supporters have \
        uttered the phrase \"wait till next year\" perhaps more than any other fans in baseball, with their team\'s \
        championship drought stretching to 107 years after being swept from this year\'s playoffs by the New York \
        Mets.</p>\n<p>However, the 2015 Cubs have given Chicago\'s north-side faithful reason to believe that \
        their wait for a title, the longest in U.S. professional sports, might soon come to an end.</p>\n<p>The \
        Mets ensured the Cubs\' unprecedented streak will continue another year with an 8-3 victory on Wednesday \
        that saw them capture the National League pennant and claim a place in the World Series against \
        Kansas City or Toronto.</p>\n<p>While the Cubs\' clubhouse was disappointed after the defeat, there were \
        real signs of hope.</p>'
        reuters_derive_dateline(item)
        self.assertEqual(item['dateline']['located']['city'], 'Chicago')

    def with_a_dateline_already_leave_it_alone_test(self):
        item = dict()
        item['firstcreated'] = datetime.datetime(2015, 10, 26, 11, 45, 19, 0)
        item['dateline'] = {'located': {'city': 'Chicargo'}}
        item['body_html'] = '<p>DONT CARE (Reuters) - Chicago Cubs supporters have \
        uttered the phrase \"wait till next year\" perhaps more than any other fans in baseball, with their team\'s \
        championship drought stretching to 107 years after being swept from this year\'s playoffs by the New York \
        Mets.</p>\n<p>However, the 2015 Cubs have given Chicago\'s north-side faithful reason to believe that \
        their wait for a title, the longest in U.S. professional sports, might soon come to an end.</p>\n<p>The \
        Mets ensured the Cubs\' unprecedented streak will continue another year with an 8-3 victory on Wednesday \
        that saw them capture the National League pennant and claim a place in the World Series against \
        Kansas City or Toronto.</p>\n<p>While the Cubs\' clubhouse was disappointed after the defeat, there were \
        real signs of hope.</p>'
        reuters_derive_dateline(item)
        self.assertEqual(item['dateline']['located']['city'], 'Chicargo')

    def with_just_a_date_test(self):
        item = dict()
        item['firstcreated'] = datetime.datetime(2015, 10, 26, 11, 45, 19, 0)
        item['body_html'] = '<p>Oct 22 (Reuters) - Eurotunnel said on\nThursday that third-quarter revenue \
        rose 3 percent to 334.4\nmillion euros ($379.48 million), as economic recovery helped\noffset the \
        impact of the disruption to traffic resulting from\nthe migrant crisis.</p>\n<p>The operator of the \
        Channel Tunnel linking France and\nBritain said that business remained dynamic, driven by a\nrecovering \
        economy in Britain and to a lesser extent in the\neuro-zone.</p>'
        reuters_derive_dateline(item)
        self.assertNotIn('dateline', item)

    def from_bagalore_test(self):
        item = {'dateline': {'located': {'city': 'Bangalore'}}}
        item['firstcreated'] = datetime.datetime(2015, 10, 26, 11, 45, 19, 0)
        item['body_html'] = '<p>Wagga Wagga (Reuters) - Chicago Cubs supporters have \
        uttered the phrase \"wait till next year\" perhaps more than any other fans in baseball, with their team\'s \
        championship drought stretching to 107 years after being swept from this year\'s playoffs by the New York \
        Mets.</p>\n<p>However, the 2015 Cubs have given Chicago\'s north-side faithful reason to believe that \
        their wait for a title, the longest in U.S. professional sports, might soon come to an end.</p>\n<p>The \
        Mets ensured the Cubs\' unprecedented streak will continue another year with an 8-3 victory on Wednesday \
        that saw them capture the National League pennant and claim a place in the World Series against \
        Kansas City or Toronto.</p>\n<p>While the Cubs\' clubhouse was disappointed after the defeat, there were \
        real signs of hope.</p>'
        reuters_derive_dateline(item)
        self.assertEqual(item['dateline']['located']['city'], 'Wagga Wagga')
