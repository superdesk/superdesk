
import logging

from flask import current_app as app
from superdesk import get_resource_service
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
    if renditions and not dry:
        logger.info('Removing %d media files for item %s', len(renditions), item.get('guid'))
    elif not dry:
        logger.info('No media to be removed for item %s', item.get('guid'))

    # remove media references for the item
    get_resource_service('media_references').delete_action(lookup={
        'item_id': item['item_id'],
    })

    for rend in renditions:
        try:
            if not dry:
                references = get_resource_service('media_references').get(req=None, lookup={
                    'media_id': str(rend['media']),
                })

                if references.count() == 0:
                    logger.info('removing %s', rend['media'])
                    app.media.delete(str(rend['media']))
                else:
                    logger.info('keeping %s due to references')
            else:
                print(rend['media'])
        except Exception:
            logger.exception('Failed to remove media %s', rend['media'])
            continue


def init_app(_app):
    archived_item_removed.connect(remove_expired_media)
