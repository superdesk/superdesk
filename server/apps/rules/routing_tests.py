# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


from superdesk.tests import TestCase
from apps.rules.routing_rule_validator import RoutingRuleValidator


class RoutingRuleValidatorTestCase(TestCase):
    def setUp(self):
        self.items = [
            {
                '_id': 'item1',
                'anpa_category': [{'qcode': 'e'}],
                'subject': [{'qcode': '01000000'}, {'qcode': '01001000'}],
                'headline': 'this is about Kate Williams.',
                'slugline': 'Kate Williams',
                'body_html': 'this is about Kate Williams trip to Bondi Beach.',
                'type': 'text',
                'genre': ['story']
            },
            {
                '_id': 'item2',
                'anpa_category': [{'qcode': 'e'}],
                'subject': [{'qcode': '01000000'}, {'qcode': '01001000'}],
                'headline': 'this is about Robin Williams.',
                'slugline': 'Robin Williams',
                'body_html': 'this is about Robin Williams trip to Bondi Beach.',
                'type': 'text',
                'genre': ['sidebar']
            },
            {
                '_id': 'item3',
                'anpa_category': [{'qcode': 's'}],
                'subject': [{'qcode': '04000000'}, {'qcode': '04001000'}],
                'headline': 'This is about Michael Clarke.',
                'slugline': 'WC15 Clarke',
                'body_html': 'Michael Clarke scored 1000 runs in World Cup 2015.',
                'type': 'text',
                'genre': ['factbox']
            },
            {
                "_id": "item4",
                "subject":
                [
                    {"name": "sport", "qcode": "15000000"},
                    {"name": "tennis", "qcode": "15065000"}
                ],
                "genre": [],
                'anpa_category': [{'qcode': 's'}],
                "urgency": "4",
                "type": "picture",
                "description": "Casey Williamson of Australia stretches to reach a shot against Madison Keys.",
                "slugline": "Tennis WC15 Casey",
                "headline": "Williamson of Australia stretches to reach a shot against Keys.",
                "source": "reuters"
            },
            {
                '_id': 'item5',
                'anpa_category': [{'qcode': 's'}],
                'subject': [{"name": "sport", "qcode": "15000000"}],
                'headline': 'Australia won the world cup.',
                'slugline': 'WC15 Final',
                'body_html': 'Australia won the world cup fifth time.',
                'type': 'text',
                'genre': ['sidebar']
            }
        ]

    def test_rule_for_anpa_category_e_or_s_and_genre_sidebar(self):
        rule_filter = {
            'category': [{'qcode': 'e'}, {'qcode': 's'}],
            'genre': ['sidebar']
        }

        validator = RoutingRuleValidator()
        self.assertFalse(validator.is_valid_rule(self.items[0], rule_filter))
        self.assertTrue(validator.is_valid_rule(self.items[1], rule_filter))
        self.assertFalse(validator.is_valid_rule(self.items[2], rule_filter))
        self.assertFalse(validator.is_valid_rule(self.items[3], rule_filter))
        self.assertTrue(validator.is_valid_rule(self.items[4], rule_filter))

    def test_rule_for_subject_sport_and_body_australia(self):
        rule_filter = {
            'subject': [{'qcode': '15000000'}],
            'body': 'Australia'
        }

        validator = RoutingRuleValidator()
        self.assertFalse(validator.is_valid_rule(self.items[0], rule_filter))
        self.assertFalse(validator.is_valid_rule(self.items[1], rule_filter))
        self.assertFalse(validator.is_valid_rule(self.items[2], rule_filter))
        self.assertFalse(validator.is_valid_rule(self.items[3], rule_filter))
        self.assertTrue(validator.is_valid_rule(self.items[4], rule_filter))

    def test_rule_for_body_williams(self):
        rule_filter = {
            'headline': 'williams'
        }

        validator = RoutingRuleValidator()
        self.assertTrue(validator.is_valid_rule(self.items[0], rule_filter))
        self.assertTrue(validator.is_valid_rule(self.items[1], rule_filter))
        self.assertFalse(validator.is_valid_rule(self.items[2], rule_filter))
        self.assertTrue(validator.is_valid_rule(self.items[3], rule_filter))
        self.assertFalse(validator.is_valid_rule(self.items[4], rule_filter))

    def test_rule_for_body_williams_exact(self):
        rule_filter = {
            'headline': '\\bwilliams\\b'
        }

        validator = RoutingRuleValidator()
        self.assertTrue(validator.is_valid_rule(self.items[0], rule_filter))
        self.assertTrue(validator.is_valid_rule(self.items[1], rule_filter))
        self.assertFalse(validator.is_valid_rule(self.items[2], rule_filter))
        self.assertFalse(validator.is_valid_rule(self.items[3], rule_filter))
        self.assertFalse(validator.is_valid_rule(self.items[4], rule_filter))

    def test_rule_for_slugline_startswith_WC15(self):
        rule_filter = {
            'slugline': '^WC15 '
        }

        validator = RoutingRuleValidator()
        self.assertFalse(validator.is_valid_rule(self.items[0], rule_filter))
        self.assertFalse(validator.is_valid_rule(self.items[1], rule_filter))
        self.assertTrue(validator.is_valid_rule(self.items[2], rule_filter))
        self.assertFalse(validator.is_valid_rule(self.items[3], rule_filter))
        self.assertTrue(validator.is_valid_rule(self.items[4], rule_filter))

    def test_rule_for_slugline_startswith_WC15_genre_sidebar_or_factbox(self):
        rule_filter = {
            'slugline': '^WC15 ',
            'genre': ['sidebar', 'factbox']
        }

        validator = RoutingRuleValidator()
        self.assertFalse(validator.is_valid_rule(self.items[0], rule_filter))
        self.assertFalse(validator.is_valid_rule(self.items[1], rule_filter))
        self.assertTrue(validator.is_valid_rule(self.items[2], rule_filter))
        self.assertFalse(validator.is_valid_rule(self.items[3], rule_filter))
        self.assertTrue(validator.is_valid_rule(self.items[4], rule_filter))
