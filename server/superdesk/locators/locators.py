# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from operator import itemgetter

from eve.render import send_response
from flask.blueprints import Blueprint

import superdesk
from superdesk.utc import utcnow
from superdesk.locators import locators

bp = Blueprint('locators', __name__)


@bp.route('/cities/', methods=['GET', 'OPTIONS'])
@bp.route('/country/<country_code>', methods=['GET', 'OPTIONS'])
@bp.route('/country/<country_code>/state/<state_code>', methods=['GET', 'OPTIONS'])
def get_cities(country_code=None, state_code=None):
    """
    Fetches cities and sends the list as response body.

    :param  country_code: Country Code as defined in the locators.json file.
            For example, AU for Australia, NZ for New Zealand.
    :param state_code: State Code as defined in the locators.json file. For example, VIC for Victoria, NV for Nevada.
    :return:
        Returns HTTP Response with body {'_items': cities, '_meta': {'total': City Count}}.
    """

    cities = find_cities(country_code=country_code, state_code=state_code)

    if cities and len(cities):
        response_data = {'_items': cities, '_meta': {'total': len(cities)}}
        return send_response(None, (response_data, utcnow(), None, 200))
    else:
        return send_response(None, ({}, utcnow(), None, 404))


def find_cities(country_code=None, state_code=None):
    """
    Fetches cities in the locators.json file.

    Returns all the cities in the locators.json file.
    When country_code is passed it gets cities in the country identified by country_code.

    :param  country_code: Country Code as defined in the locators.json file.
            For example, AU for Australia, NZ for New Zealand.
    :param state_code: State Code as defined in the locators.json file. For example, VIC for Victoria, NV for Nevada.
    :return:
        Returns Cities in a State when both country_code and state_code are passed.
        Returns Cities in a Country when only country_code is passed.
        Returns Cities across all countries when nothing is passed.
    """

    if country_code and state_code:
        cities = [{'city_code': city['qcode'], 'city': city['name'], 'alt_name': city.get('alt_name', ''),
                   'tz': city['timezone'], 'dateline': city['dateline_format'], 'state': state['name'],
                   'state_code': state['qcode'], 'country': country['name'], 'country_code': country['qcode']}
                  for country in locators if country['qcode'] == country_code
                  for state in country['states'] if state['qcode'] == state_code for city in state['cities']]
        cities.sort(key=itemgetter('city'))
    elif country_code:
        cities = [{'city_code': city['qcode'], 'city': city['name'], 'alt_name': city.get('alt_name', ''),
                   'tz': city['timezone'], 'dateline': city['dateline_format'], 'state': state['name'],
                   'state_code': state['qcode'], 'country': country['name'], 'country_code': country['qcode']}
                  for country in locators if country['qcode'] == country_code for state in country['states']
                  for city in state['cities']]
        cities.sort(key=itemgetter('state', 'city'))
    else:
        cities = [{'city_code': city['qcode'], 'city': city['name'], 'alt_name': city.get('alt_name', ''),
                   'tz': city['timezone'], 'dateline': city['dateline_format'], 'state': state['name'],
                   'state_code': state['qcode'], 'country': country['name'], 'country_code': country['qcode']}
                  for country in locators for state in country['states'] for city in state['cities']]
        cities.sort(key=itemgetter('country', 'state', 'city'))

    return cities


superdesk.blueprint(bp)
