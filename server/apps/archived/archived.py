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

from flask import current_app as app
from eve.utils import config, ParsedRequest
import logging

from eve.versioning import resolve_document_version

from apps.legal_archive.commands import import_into_legal_archive
from apps.legal_archive.resource import LEGAL_PUBLISH_QUEUE_NAME
from apps.packages.takes_package_service import TakesPackageService
from apps.publish.content.common import ITEM_KILL
from apps.publish.content.kill import KillPublishService
from apps.publish.published_item import published_item_fields
from apps.packages import PackageService
from superdesk import get_resource_service
from superdesk.errors import SuperdeskApiError
from superdesk.metadata.utils import aggregations
from superdesk.metadata.item import CONTENT_TYPE, ITEM_TYPE, not_analyzed, GUID_FIELD, ITEM_STATE, CONTENT_STATE, \
    PUB_STATUS
from superdesk.metadata.packages import PACKAGE_TYPE, TAKES_PACKAGE, RESIDREF, SEQUENCE, GROUPS, REFS
from superdesk.notification import push_notification
from apps.archive.common import get_user, item_schema, is_genre, BROADCAST_GENRE, ITEM_OPERATION, is_item_in_package, \
    insert_into_versions
from apps.archive.archive import SOURCE as ARCHIVE
import superdesk
from superdesk.services import BaseService
from superdesk.resource import Resource
from superdesk.utc import utcnow

logger = logging.getLogger(__name__)


class ArchivedResource(Resource):
    datasource = {
        'search_backend': 'elastic',
        'aggregations': aggregations,
        'default_sort': [('_updated', -1)],
        'projection': {
            'old_version': 0,
            'last_version': 0
        }
    }

    mongo_prefix = 'ARCHIVED'

    extra_fields = published_item_fields.copy()
    # item_id + _current_version will be used fetch archived item.
    extra_fields['archived_id'] = {
        'type': 'string',
        'mapping': not_analyzed
    }

    schema = item_schema(extra_fields)
    resource_methods = ['GET']
    item_methods = ['GET', 'DELETE']
    privileges = {'DELETE': 'archived'}

    additional_lookup = {
        'url': 'regex("[\w,.:-]+")',
        'field': 'archived_id'
    }


class ArchivedService(BaseService):

    def on_create(self, docs):
        package_service = PackageService()

        for doc in docs:
            doc.pop('lock_user', None)
            doc.pop('lock_time', None)
            doc.pop('lock_session', None)
            doc['archived_id'] = self._get_archived_id(doc.get('item_id'), doc.get(config.VERSION))

            if doc.get(ITEM_TYPE) == CONTENT_TYPE.COMPOSITE:
                is_takes_package = doc.get(PACKAGE_TYPE) == TAKES_PACKAGE
                for ref in package_service.get_item_refs(doc):
                    ref['location'] = 'archived'

                    if is_takes_package and not ref.get('is_published'):
                        # if take is not published
                        package_service.remove_ref_from_inmem_package(doc, ref.get(RESIDREF))

                if is_takes_package:
                    doc[SEQUENCE] = len(package_service.get_item_refs(doc))

    def on_delete(self, doc):
        """
        Overriding to validate the item being killed is actually eligible for kill. Validates the following:
            1. Is item of type Text?
            2. Is item a Broadcast Script?
            3. Does item acts as a Master Story for any of the existing broadcasts?
            4. Is item available in production or part of a normal package?
            5. Is the associated Digital Story is available in production or part of normal package?
            6. If item is a Take then is any take available in production or part of normal package?
        :param doc: represents the article in archived collection
        :type doc: dict
        :raises SuperdeskApiError.badRequestError() if any of the above validation conditions fail.
        """

        bad_req_error = SuperdeskApiError.badRequestError

        id_field = doc[config.ID_FIELD]
        item_id = doc['item_id']

        doc['item_id'] = id_field
        doc[config.ID_FIELD] = item_id

        if doc[ITEM_TYPE] != CONTENT_TYPE.TEXT:
            raise bad_req_error(message='Only Text articles are allowed to Kill in Archived repo')

        if is_genre(doc, BROADCAST_GENRE):
            raise bad_req_error(message="Killing of Broadcast Items isn't allowed in Archived repo")

        if get_resource_service('archive_broadcast').get_broadcast_items_from_master_story(doc, True):
            raise bad_req_error(message="Can't kill as this article acts as a Master Story for existing broadcast(s)")

        if get_resource_service(ARCHIVE).find_one(req=None, _id=doc[GUID_FIELD]):
            raise bad_req_error(message="Can't Kill as article is still available in production")

        if is_item_in_package(doc):
            raise bad_req_error(message="Can't kill as article is part of a Package")

        takes_package_service = TakesPackageService()
        takes_package_id = takes_package_service.get_take_package_id(doc)
        if takes_package_id:
            if get_resource_service(ARCHIVE).find_one(req=None, _id=takes_package_id):
                raise bad_req_error(message="Can't Kill as the Digital Story is still available in production")

            req = ParsedRequest()
            req.sort = '[("%s", -1)]' % config.VERSION
            takes_package = list(self.get(req=req, lookup={'item_id': takes_package_id}))
            if not takes_package:
                raise bad_req_error(message='Digital Story of the article not found in Archived repo')

            takes_package = takes_package[0]
            if is_item_in_package(takes_package):
                raise bad_req_error(message="Can't kill as Digital Story is part of a Package")

            for takes_ref in takes_package_service.get_package_refs(takes_package):
                if takes_ref[RESIDREF] != doc[GUID_FIELD]:
                    if get_resource_service(ARCHIVE).find_one(req=None, _id=takes_ref[RESIDREF]):
                        raise bad_req_error(message="Can't Kill as Take(s) are still available in production")

                    take = list(self.get(req=None, lookup={'item_id': takes_ref[RESIDREF]}))
                    if not take:
                        raise bad_req_error(message='One of Take(s) not found in Archived repo')

                    if is_item_in_package(take[0]):
                        raise bad_req_error(message="Can't kill as one of Take(s) is part of a Package")

        doc['item_id'] = item_id
        doc[config.ID_FIELD] = id_field

    def delete(self, lookup):
        """
        Overriding to handle with Kill workflow in the Archived repo:
            1. Check if Article has an associated Digital Story and if Digital Story has more Takes.
               If both Digital Story and more Takes exists then all of them would be killed along with the one requested
            2. For each article being killed do the following:
                i.   Apply the Kill Template and create an entry in archive, archive_versions and published collections.
                ii.  Query the Publish Queue in Legal Archive and find the subscribers who received the article
                     previously and create transmission entries in Publish Queue.
                iii. Change the state of the article to Killed in Legal Archive.
                iv.  Delete all the published versions from Archived.
                v.   Send a broadcast email to all subscribers.
        :param lookup: query to find the article in archived repo
        :type lookup: dict
        """

        if app.testing and len(lookup) == 0:
            super().delete(lookup)
            return

        # Step 1
        articles_to_kill = self._find_articles_to_kill(lookup)
        articles_to_kill.sort(key=itemgetter(ITEM_TYPE), reverse=True)  # Needed because package has to be inserted last
        kill_service = KillPublishService()

        for article in articles_to_kill:
            # Step 2(i)
            to_apply_template = {'template_name': 'kill', 'item': article}
            get_resource_service('content_templates_apply').post([to_apply_template])
            article = to_apply_template['item']
            self._remove_and_set_kill_properties(article, articles_to_kill)

            # Step 2(ii)
            transmission_details = list(
                get_resource_service(LEGAL_PUBLISH_QUEUE_NAME).get(req=None,
                                                                   lookup={'item_id': article[config.ID_FIELD]}))

            if transmission_details:
                subscriber_ids = [t['_subscriber_id'] for t in transmission_details]
                query = {'$and': [{config.ID_FIELD: {'$in': subscriber_ids}}]}
                subscribers = list(get_resource_service('subscribers').get(req=None, lookup=query))

                kill_service.queue_transmission(article, subscribers)

            # Step 2(iii)
            import_into_legal_archive.apply_async(kwargs={'doc': article})

            # Step 2(iv)
            super().delete({'item_id': article[config.ID_FIELD]})

            # Step 2(i) - Creating entries in published collection
            docs = [article]
            get_resource_service(ARCHIVE).post(docs)
            insert_into_versions(doc=article)
            get_resource_service('published').post(docs)

            # Step 2(v)
            kill_service.broadcast_kill_email(article)

    def on_deleted(self, doc):
        user = get_user()
        push_notification('item:deleted:archived', item=str(doc[config.ID_FIELD]), user=str(user.get(config.ID_FIELD)))

    def on_fetched_item(self, doc):
        doc['_type'] = 'archived'

    def _get_archived_id(self, item_id, version):
        return '{}:{}'.format(item_id, version)

    def _find_articles_to_kill(self, lookup):
        """
        Finds the article to kill. If the article is associated with Digital Story then Digital Story will
        also be fetched. If the Digital Story has more takes then all of them would be fetched.

        :param lookup: query to find the main article to be killed
        :type lookup: dict
        :return: list of articles to be killed
        :rtype: list
        """

        archived_doc = self.find_one(req=None, **lookup)

        req = ParsedRequest()
        req.sort = '[("%s", -1)]' % config.VERSION

        archived_doc = list(self.get(req=req, lookup={'item_id': archived_doc['item_id']}))[0]
        articles_to_kill = [archived_doc]
        takes_package_service = TakesPackageService()
        takes_package_id = takes_package_service.get_take_package_id(archived_doc)
        if takes_package_id:
            takes_package = list(self.get(req=req, lookup={'item_id': takes_package_id}))[0]
            articles_to_kill.append(takes_package)

            for takes_ref in takes_package_service.get_package_refs(takes_package):
                if takes_ref[RESIDREF] != archived_doc[GUID_FIELD]:
                    take = list(self.get(req=req, lookup={'item_id': takes_ref[RESIDREF]}))[0]
                    articles_to_kill.append(take)

        return articles_to_kill

    def _remove_and_set_kill_properties(self, article, articles_to_kill):
        """
        Removes the irrelevant properties from the given article and sets the properties for kill operation.

        :param article: article from the archived repo
        :type article: dict
        :param articles_to_kill: list of articles which were about to kill from dusty archive
        :type articles_to_kill: list
        """

        article[config.ID_FIELD] = article.pop('item_id', article['item_id'])

        article.pop('allow_post_publish_actions', None)
        article.pop('can_be_removed', None)
        article.pop('archived_id', None)
        article.pop('_type', None)
        article.pop('_links', None)
        article.pop(config.ETAG, None)

        article[ITEM_STATE] = CONTENT_STATE.KILLED
        article[ITEM_OPERATION] = ITEM_KILL
        article['pubstatus'] = PUB_STATUS.CANCELED
        article[config.LAST_UPDATED] = utcnow()

        user = get_user()
        article['version_creator'] = str(user[config.ID_FIELD])

        resolve_document_version(article, ARCHIVE, 'PATCH', article)

        if article[ITEM_TYPE] == CONTENT_TYPE.COMPOSITE:
            for group in article.get(GROUPS, []):
                for ref in group.get(REFS, []):
                    if RESIDREF in ref:
                        item_in_package = [item for item in articles_to_kill if item.get('item_id') == ref[RESIDREF]]
                        ref['location'] = ARCHIVE
                        ref[config.VERSION] = item_in_package[0][config.VERSION]


superdesk.privilege(name='archived', label='Archived Management', description='User can remove items from the archived')
