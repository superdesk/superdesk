import logging
import superdesk

from superdesk.signals import item_publish
from superdesk.metadata.item import PUBLISH_STATES

from .constants import PRODUCTS_ID

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def on_update(resource, updates, original):
    if resource == 'archive_publish':
        on_publish(updates, original)
        return


def on_publish(updates, original):
    assign_product_to_pictures(updates, original)
    unlink_update_on_auto_publish(updates, original)


def unlink_update_on_auto_publish(updates, original):
    """
    Unlink auto published item when original is not published yet.

    SDANSA-385
    """
    if not updates.get('auto_publish'):
        return

    updated = original.copy()
    updated.update(updates)

    if updated.get('rewrite_of'):
        main = superdesk.get_resource_service('archive').find_one(req=None, _id=updated['rewrite_of'])
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


def assign_product_to_pictures(updates, original):
    """When item is published with associated pictures
    make sure these have product assigned.
    """
    associations = updates.get('associations')
    if not associations:
        return
    for key, item in associations.items():
        if not item or item.get('type') != 'picture' or item.get('state') in PUBLISH_STATES:
            continue
        subject = item.setdefault('subject', [])
        product = next((subj for subj in subject if subj.get('scheme') == PRODUCTS_ID), None)
        if not product:
            subject.append({
                'name': 'Browser Allegati',
                'qcode': '0050000100002',
                'scheme': PRODUCTS_ID,
            })
        item['auto_publish'] = True
        if original:
            original.setdefault('associations', {}).update({key: item})


def udpate_sign_off(sender, item, **kwargs):
    """When item is auto published add -RED to sign_off."""
    if item.get('auto_publish'):
        if not item.get('sign_off'):
            item['sign_off'] = 'RED'


def init_app(app):
    superdesk.privilege(
        name='ansa_metasearch',
        label='ANSA - metasearch',
        decsription=''
    )

    superdesk.privilege(
        name='ansa_live_assistant',
        label='ANSA - live assistant',
        decsription=''
    )

    superdesk.privilege(
        name='ansa_ai_news',
        label='ANSA - ai news',
        decsription=''
    )

    app.on_update += on_update
    item_publish.connect(udpate_sign_off)
