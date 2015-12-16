# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from flask import current_app as app
from superdesk.errors import SuperdeskApiError
from superdesk.resource import Resource
from superdesk import config
from superdesk.utils import SuperdeskBaseEnum
from bson.objectid import ObjectId
from superdesk.services import BaseService
import superdesk
from superdesk.notification import push_notification
from superdesk.activity import add_activity, ACTIVITY_UPDATE
from superdesk.metadata.item import FAMILY_ID
from eve.utils import ParsedRequest


class DeskTypes(SuperdeskBaseEnum):
    authoring = 'authoring'
    production = 'production'


desks_schema = {
    'name': {
        'type': 'string',
        'required': True,
        'nullable': False,
        'empty': False,
        'iunique': True
    },
    'description': {
        'type': 'string'
    },
    'members': {
        'type': 'list',
        'schema': {
            'type': 'dict',
            'schema': {
                'user': Resource.rel('users', True)
            }
        }
    },
    'incoming_stage': Resource.rel('stages', True),
    'working_stage': Resource.rel('stages', True),
    'content_expiry': {
        'type': 'integer'
    },
    'source': {
        'type': 'string'
    },
    'monitoring_settings': {
        'type': 'list',
        'schema': {
            'type': 'dict',
            'schema': {
                '_id': {
                    'type': 'string',
                    'required': True
                },
                'type': {
                    'type': 'string',
                    'allowed': ['search', 'stage', 'deskOutput', 'personal'],
                    'required': True
                },
                'max_items': {
                    'type': 'integer',
                    'required': True
                }
            }
        }
    },
    'desk_type': {
        'type': 'string',
        'default': DeskTypes.authoring.value,
        'allowed': DeskTypes.values()
    }
}


def init_app(app):
    endpoint_name = 'desks'
    service = DesksService(endpoint_name, backend=superdesk.get_backend())
    DesksResource(endpoint_name, app=app, service=service)
    endpoint_name = 'user_desks'
    service = UserDesksService(endpoint_name, backend=superdesk.get_backend())
    UserDesksResource(endpoint_name, app=app, service=service)
    endpoint_name = 'sluglines'
    service = SluglineDeskService(endpoint_name, backend=superdesk.get_backend())
    SluglineDesksResource(endpoint_name, app=app, service=service)


superdesk.privilege(name='desks', label='Desk Management', description='User can manage desks.')


class DesksResource(Resource):
    schema = desks_schema
    privileges = {'POST': 'desks', 'PATCH': 'desks', 'DELETE': 'desks'}


class DesksService(BaseService):
    notification_key = 'desk'

    def create(self, docs, **kwargs):
        """
        Overriding to check if the desk being created has Working and Incoming Stages. If not then Working and Incoming
        Stages would be created and associates them with the desk and desk with the Working and Incoming Stages.
        Also sets desk_type.

        :return: list of desk id's
        """

        for desk in docs:
            stages_to_be_linked_with_desk = []
            stage_service = superdesk.get_resource_service('stages')

            if desk.get('content_expiry') == 0:
                desk['content_expiry'] = app.settings['CONTENT_EXPIRY_MINUTES']

            if 'working_stage' not in desk:
                stages_to_be_linked_with_desk.append('working_stage')
                stage_id = stage_service.create_working_stage()
                desk['working_stage'] = stage_id[0]

            if 'incoming_stage' not in desk:
                stages_to_be_linked_with_desk.append('incoming_stage')
                stage_id = stage_service.create_incoming_stage()
                desk['incoming_stage'] = stage_id[0]

            desk.setdefault('desk_type', DeskTypes.authoring.value)
            super().create([desk], **kwargs)
            for stage_type in stages_to_be_linked_with_desk:
                stage_service.patch(desk[stage_type], {'desk': desk[config.ID_FIELD]})

        return [doc[config.ID_FIELD] for doc in docs]

    def on_created(self, docs):
        for doc in docs:
            push_notification(self.notification_key, created=1, desk_id=str(doc.get(config.ID_FIELD)))

    def on_update(self, updates, original):
        if updates.get('content_expiry') == 0:
            updates['content_expiry'] = None

        if updates.get('desk_type') and updates.get('desk_type') != original.get('desk_type', ''):
            archive_versions_query = {
                '$or': [
                    {'task.last_authoring_desk': str(original[config.ID_FIELD])},
                    {'task.last_production_desk': str(original[config.ID_FIELD])}
                ]
            }

            items = superdesk.get_resource_service('archive_versions').get(req=None, lookup=archive_versions_query)
            if items and items.count():
                raise SuperdeskApiError.badRequestError(
                    message='Cannot update Desk Type as there are article(s) referenced by the Desk.')

    def on_updated(self, updates, original):
        self.__send_notification(updates, original)

    def on_delete(self, desk):
        """
        Overriding to prevent deletion of a desk if the desk meets one of the below conditions:
            1. The desk isn't assigned as a default desk to user(s)
            2. The desk has no content
            3. The desk is associated with routing rule(s)
        """

        as_default_desk = superdesk.get_resource_service('users').get(req=None, lookup={'desk': desk[config.ID_FIELD]})
        if as_default_desk and as_default_desk.count():
            raise SuperdeskApiError.preconditionFailedError(
                message='Cannot delete desk as it is assigned as default desk to user(s).')

        routing_rules_query = {
            '$or': [
                {'rules.actions.fetch.desk': desk[config.ID_FIELD]},
                {'rules.actions.publish.desk': desk[config.ID_FIELD]}
            ]
        }
        routing_rules = superdesk.get_resource_service('routing_schemes').get(req=None, lookup=routing_rules_query)
        if routing_rules and routing_rules.count():
            raise SuperdeskApiError.preconditionFailedError(
                message='Cannot delete desk as routing scheme(s) are associated with the desk')

        archive_versions_query = {
            '$or': [
                {'task.desk': str(desk[config.ID_FIELD])},
                {'task.last_authoring_desk': str(desk[config.ID_FIELD])},
                {'task.last_production_desk': str(desk[config.ID_FIELD])}
            ]
        }

        items = superdesk.get_resource_service('archive_versions').get(req=None, lookup=archive_versions_query)
        if items and items.count():
            raise SuperdeskApiError.preconditionFailedError(
                message='Cannot delete desk as it has article(s) or referenced by versions of the article(s).')

    def delete(self, lookup):
        """
        Overriding to delete stages before deleting a desk
        """

        superdesk.get_resource_service('stages').delete(lookup={'desk': lookup.get(config.ID_FIELD)})
        super().delete(lookup)

    def on_deleted(self, doc):
        desk_user_ids = [str(member['user']) for member in doc.get('members', [])]
        push_notification(self.notification_key,
                          deleted=1,
                          user_ids=desk_user_ids,
                          desk_id=str(doc.get(config.ID_FIELD)))

    def __compare_members(self, original, updates):
        original_members = set([member['user'] for member in original])
        updates_members = set([member['user'] for member in updates])
        added = updates_members - original_members
        removed = original_members - updates_members
        return added, removed

    def __send_notification(self, updates, desk):
        desk_id = desk[config.ID_FIELD]

        if 'members' in updates:
            added, removed = self.__compare_members(desk.get('members', {}), updates['members'])
            if len(removed) > 0:
                push_notification('desk_membership_revoked',
                                  updated=1,
                                  user_ids=[str(item) for item in removed],
                                  desk_id=str(desk_id))

            for added_user in added:
                user = superdesk.get_resource_service('users').find_one(req=None, _id=added_user)
                add_activity(ACTIVITY_UPDATE,
                             'user {{user}} has been added to desk {{desk}}: Please re-login.',
                             self.datasource,
                             notify=added,
                             user=user.get('username'),
                             desk=desk.get('name'))
        else:
            push_notification(self.notification_key, updated=1, desk_id=str(desk.get(config.ID_FIELD)))


class UserDesksResource(Resource):
    url = 'users/<regex("[a-f0-9]{24}"):user_id>/desks'
    schema = desks_schema
    datasource = {'source': 'desks', 'default_sort': [('name', 1)]}
    resource_methods = ['GET']


class UserDesksService(BaseService):

    def get(self, req, lookup):
        if lookup.get('user_id'):
            lookup['members.user'] = ObjectId(lookup['user_id'])
            del lookup['user_id']
        return super().get(req, lookup)

    def is_member(self, user_id, desk_id):
        # desk = list(self.get(req=None, lookup={'members.user':ObjectId(user_id), '_id': ObjectId(desk_id)}))
        return len(list(self.get(req=None, lookup={'members.user': ObjectId(user_id), '_id': ObjectId(desk_id)}))) > 0


class SluglineDesksResource(Resource):

    url = 'desks/<regex("[a-f0-9]{24}"):desk_id>/sluglines'
    datasource = {'source': 'published',
                  'search_backend': 'elastic',
                  'default_sort': [('slugline.phrase', 1), ("versioncreated", 0)],
                  'elastic_filter': {"and": [{"range": {"versioncreated": {"gte": "now-24H"}}},
                                             {"term": {"last_published_version": True}},
                                             {"term": {"type": "text"}}
                                             ]}}
    resource_methods = ['GET']
    item_methods = []


class SluglineDeskService(BaseService):
    SLUGLINE = 'slugline'
    OLD_SLUGLINES = 'old_sluglines'
    VERSION_CREATED = 'versioncreated'
    HEADLINE = 'headline'
    NAME = 'name'
    PLACE = 'place'
    GROUP = 'group'

    def _get_slugline_with_legal(self, article):
        """
        If the article is set to be legal adds 'Legal:' prefix for slugline
        :param article:
        :return:
        """
        is_legal = article.get('flags', {}).get('marked_for_legal', False)
        if is_legal:
            return '{}: {}'.format('Legal', article.get(self.SLUGLINE, ''))
        else:
            return article.get(self.SLUGLINE, '')

    def get(self, req, lookup):
        """
        Given the desk the function will return a summary of the sluglines and headlines published from that
        desk in the last 24 hours. Domestic items are grouped together, rest of the world items are group
        by their place names.
        :param req:
        :param lookup:
        :return:
        """
        lookup['task.desk'] = lookup['desk_id']
        lookup.pop('desk_id')
        req.max_results = 1000
        desk_items = super().get(req, lookup)

        # domestic docs
        docs = []
        # rest of the world docs
        row_docs = []
        for item in desk_items:
            slugline = self._get_slugline_with_legal(item)
            headline = item.get(self.HEADLINE)
            versioncreated = item.get(self.VERSION_CREATED)
            placename = 'Domestic'
            # Determine if the item is either domestic or rest of the world
            if self.PLACE in item and len(item[self.PLACE]) > 0 and self.GROUP in item.get(self.PLACE)[0] \
                    and item.get(self.PLACE)[0][self.GROUP] == 'Rest Of World':
                row = True
                placename = item.get(self.PLACE)[0].get(self.NAME, 'Domestic')
            else:
                row = False
            # Find if there are other sluglines in this items family
            newer, older_slugline = self._find_other_sluglines(item.get(FAMILY_ID), slugline,
                                                               item.get(self.VERSION_CREATED))
            # there are no newer sluglines than the current one
            if not newer:
                if row:
                    self._add_slugline_to_places(row_docs, placename, slugline, headline, older_slugline,
                                                 versioncreated)
                else:
                    self._add_slugline_to_places(docs, placename, slugline, headline, older_slugline, versioncreated)

        docs.extend(row_docs)
        desk_items.docs = docs
        return desk_items

    def _add_slugline_to_places(self, places, placename, slugline, headline, old_sluglines, versioncreated):
        """
        Append a dictionary to the list, with place holders for the place name and slugline if they are already
        present
        :param places:
        :param placename:
        :param slugline:
        :param headline:
        :param is_legal:
        :param old_sluglines:
        :param versioncreated:
        :return:
        """
        places.append({self.NAME: placename if not any(p[self.NAME] == placename for p in places) else '-',
                       self.SLUGLINE: slugline if not any(self._get_slugline_with_legal(p).lower() == slugline.lower()
                                                          for p in places) else '-',
                       self.HEADLINE: headline,
                       self.OLD_SLUGLINES: old_sluglines,
                       self.VERSION_CREATED: versioncreated})

    def _find_other_sluglines(self, family_id, slugline, versioncreated):
        """
        This function given a family_id will return a tuple with the first value true if there is
         a more recent story in the family, the second value in the tuple will be a list of any sluglines
         that might exist for the family that are different to the one passed.
        :param family_id:
        :param slugline:
        :param versioncreated:
        :return: A tuple as described above
        """
        older_sluglines = []
        req = ParsedRequest()
        lookup = {'family_id': family_id}
        family = superdesk.get_resource_service('published').get_from_mongo(req=req, lookup=lookup)
        for member in family:
            member_slugline = self._get_slugline_with_legal(member)
            if member_slugline.lower() != slugline.lower():
                if member.get('versioncreated') < versioncreated:
                    if member_slugline not in older_sluglines:
                        older_sluglines.append(member_slugline)
                else:
                    return (True, [])
        return (False, older_sluglines)
