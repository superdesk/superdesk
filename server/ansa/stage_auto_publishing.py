
import cerberus
import superdesk

from superdesk.logging import logger

AUTO_PUBLISH_FIELD = 'auto_publish'


def item_fetched_handler(sender, item, **kwargs):
    publish_item_on_auto_publish_stage(item)


def item_moved_handler(sender, item, **kwargs):
    publish_item_on_auto_publish_stage(item)


def publish_item_on_auto_publish_stage(item):
    stage_id = item.get('task', {}).get('stage')
    if not stage_id:
        return

    stage = superdesk.get_resource_service('stages').find_one(req=None, _id=stage_id)
    if stage and stage.get(AUTO_PUBLISH_FIELD):
        try:
            superdesk.get_resource_service('archive_publish').patch(item[superdesk.config.ID_FIELD],
                                                                    {'auto_publish': True})
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
