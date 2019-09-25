
import superdesk

from flask import current_app as app
from ansa.constants import PHOTO_CATEGORIES_ID, PRODUCTS_ID
from superdesk.utc import utcnow


ITEM_MAPPING = {
    'language': 'language',
    'slugline': 'categorySupAnsa',
    'headline': 'title_B',
    'description_text': 'description_B',
    'sign_off': 'signoff',
    'byline': 'authorName',
    'copyrightholder': 'copyrightHolder',
    'copyrightnotice': 'copyrightNotice',
    'usageterms': 'usageTerms',
    'pubstatus': 'status',
}

EXTRA_MAPPING = {
    'city': 'City',
    'nation': 'ctrName',
    'digitator': 'digitator',
    'signature': 'authorCode',
    'DateCreated': 'dateCreated',
    'DateRelease': 'releaseDate',
}


def apply_mapping(mapping, src, dest):
    if not src:
        return
    for src_key, dest_key in mapping.items():
        if src.get(src_key):
            dest[dest_key] = src[src_key]


def update_iptc_metadata(sender, item, **kwargs):
    if item.get('type') != 'picture':
        return
    try:
        original = item['renditions']['original']
    except KeyError:
        original = None
    if not original:
        return

    metadata = {'supplier': 'ANSA'}
    apply_mapping(ITEM_MAPPING, item, metadata)
    apply_mapping(EXTRA_MAPPING, item.get('extra'), metadata)

    if item.get('subject'):
        for subj in item['subject']:
            if subj.get('scheme') == PHOTO_CATEGORIES_ID and subj.get('name'):
                metadata['categoryAnsa'] = subj['name']
            if subj.get('scheme') == PRODUCTS_ID and subj.get('qcode'):
                metadata.setdefault('product', []).append(subj['qcode'])

    firstcreated = item.get('firstpublished') or utcnow()
    metadata['pubDate_N'] = firstcreated.isoformat()

    if metadata.get('status') and 'stat:' not in metadata['status']:
        metadata['status'] = 'stat:{}'.format(metadata['status'])

    original['media'] = app.media.put_metadata(original['media'], metadata)
    original['href'] = app.media.url_for_media(original['media'])


def init_app(_app):
    superdesk.item_publish.connect(update_iptc_metadata)
