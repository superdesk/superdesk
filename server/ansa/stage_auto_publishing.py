
import logging
import cerberus
import superdesk

from superdesk.metadata.item import PUBLISH_STATES

AUTO_PUBLISH_FIELD = 'auto_publish'

logger = logging.getLogger(__name__)


def item_fetched_handler(sender, item, **kwargs):
    publish_item_on_auto_publish_stage(item)


def item_moved_handler(sender, item, **kwargs):
    publish_item_on_auto_publish_stage(item)


def unlink_update_on_auto_publish(item, updates):
    """
    Unlink auto published item when original is not published yet.

    SDANSA-385
    """
    if item.get('rewrite_of'):
        main = superdesk.get_resource_service('archive').find_one(req=None, _id=item['rewrite_of'])
        if main and main.get('state') not in PUBLISH_STATES:
            # unlink published item
            updates.update({
                'rewrite_of': None,
                'anpa_take_key': None,
                'rewrite_sequence': None,
                'sequence': None,
            })

            # unlink original
            superdesk.get_resource_service('archive').system_update(main['_id'], {'rewritten_by': None}, main)


def publish_item_on_auto_publish_stage(item):
    stage_id = item.get('task', {}).get('stage')
    if not stage_id:
        return

    stage = superdesk.get_resource_service('stages').find_one(req=None, _id=stage_id)
    if stage and stage.get(AUTO_PUBLISH_FIELD):
        try:
            updates = {'auto_publish': True}
            unlink_update_on_auto_publish(item, updates)
            superdesk.get_resource_service('archive_publish').patch(item[superdesk.config.ID_FIELD], updates)
        except cerberus.cerberus.ValidationError:
            logger.error('item was not auto published item=%s stage=%s', item[superdesk.config.ID_FIELD], stage['name'])


def init_app(app):
    app.config['DOMAIN']['stages']['schema'].update({
        AUTO_PUBLISH_FIELD: {'type': 'boolean'},
    })

    app.config['SOURCES']['stages']['projection'].update({
        AUTO_PUBLISH_FIELD: 1,
    })

    superdesk.item_fetched.connect(item_fetched_handler)
    superdesk.item_moved.connect(item_moved_handler)
