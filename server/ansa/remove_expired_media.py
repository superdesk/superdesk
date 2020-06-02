
import logging

from flask import current_app as app
from superdesk.signals import archived_item_removed

logger = logging.getLogger(__name__)


def populate_renditions(renditions, item):
    if item.get('renditions'):
        for key, val in item['renditions'].items():
            if key != 'viewImage' and val and val.get('media'):
                renditions.append(val)


def remove_expired_media(archived_service, item, dry=False, **kwargs):
    other = archived_service.find_one(req=None, item_id=item['item_id'])
    if other is not None:
        logger.info('Skip removing media for item %s', item['item_id'])
        return
    renditions = []
    populate_renditions(renditions, item)
    if item.get('associations'):
        for key, val in item['associations'].items():
            if val:
                populate_renditions(renditions, val)
    if renditions and not dry:
        logger.info('Removing %d media files for item %s', len(renditions), item.get('guid'))
    elif not dry:
        logger.info('No media to be removed for item %s', item.get('guid'))
    for rend in renditions:
        try:
            if not dry:
                app.media.delete(str(rend['media']))
            else:
                print(rend['media'])
        except Exception:
            logger.exception('Failed to remove media %s', rend['media'])
            continue


def init_app(_app):
    archived_item_removed.connect(remove_expired_media)
