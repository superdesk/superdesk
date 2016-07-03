# -*- coding: utf-8; -*-
# This file is part of Superdesk.
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
#
# Author  : mugur
# Creation: 2016-07-01 01:30

from superdesk.commands.data_updates import DataUpdate


class DataUpdate(DataUpdate):
    """

    Data update for Pull Request #2149

    SDPA-436 - Publish - Story metadata validation - News
    SDPA-437 - Publish - Story metadata validation - Sport
    SDPA-438 - Publish - Story metadata validation - Real Life
    SDPA-439 - Publish - Story metadata validation - Motoring
    SDPA-440 - Publish - Story component validation - All services
    https://github.com/superdesk/superdesk/pull/2149


    Changes:

        1. initializa desk_metadata.anpa_category

    """

    resource = 'desks'
    desks_content_profiles = {'News Desk': 'news', 'Real Life Desk': 'real_life',
                              'Motoring Desk': 'motoring', 'Sport Desk': 'sport'}

    def forwards(self, mongodb_collection, mongodb_database):
        for desk_name, content_profile in self.desks_content_profiles.items():
            for desk in mongodb_collection.find({'name': desk_name}):
                desk_content_profiles = desk.get('content_profiles', {})
                if content_profile not in desk_content_profiles:
                    desk_content_profiles[content_profile] = True
                    print(mongodb_collection.update({'_id': desk['_id']}, {
                        '$set': {
                            'content_profiles': desk_content_profiles
                        }
                    }))

    def backwards(self, mongodb_collection, mongodb_database):
        for desk_name, content_profile in self.desks_content_profiles.items():
            for desk in mongodb_collection.find({'name': desk_name}):
                desk_content_profiles = desk.get('content_profiles', {})
                if content_profile in desk_content_profiles:
                    del desk_content_profiles[content_profile]
                    print(mongodb_collection.update({'_id': desk['_id']}, {
                        '$set': {
                            'content_profiles': desk_content_profiles
                        }
                    }))
