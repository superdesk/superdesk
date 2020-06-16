
import logging
import requests
import superdesk

from flask import abort
from superdesk.notification import push_notification


logger = logging.getLogger(__name__)

RESOURCE = 'ansa_archive'

DELETE_URL = 'http://bdmb.ansa.priv:8080/bdmws/bdmws/delete'
DELETE_TIMEOUT = (3, 10)


class ArchiveResource(superdesk.Resource):
    item_url = r'regex("[\w,.:_-]+")'
    item_methods = ['DELETE']
    resource_methods = []
    privileges = {'DELETE': RESOURCE}


class ArchiveService(superdesk.Service):

    def find_one(self, req, **lookup):
        doc = {}
        doc.update(lookup)
        doc.update({'_etag': req.if_match})
        return doc

    def delete(self, lookup):
        logging.info('deleting photo archive item %s', lookup['_id'])
        try:
            resp = requests.delete(DELETE_URL, params={'guid': lookup['_id']}, timeout=DELETE_TIMEOUT)
            resp.raise_for_status()
        except (requests.exceptions.BaseHTTPError, requests.exceptions.Timeout) as error:
            logger.error('http error when deleting photo archive item %s', error)
            abort(500)
        logger.info('photo archive item %s deleted', lookup['_id'])
        push_notification('item:spike', item=str(lookup['_id']))


def init_app(_app):
    superdesk.register_resource(RESOURCE, ArchiveResource, ArchiveService, privilege=RESOURCE, _app=_app)
    superdesk.privilege(
        name=RESOURCE,
        label='ANSA - Archive handling',
        description='User can manage ANSA Photo archive')
