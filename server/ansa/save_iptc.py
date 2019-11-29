
import time
import superdesk

from flask import current_app as app, request
from superdesk.utc import utcnow, get_date
from ansa.constants import PHOTO_CATEGORIES_ID, PRODUCTS_ID, EXIF_DATETIME_FORMAT
from ansa.vfs import VFSError


ITEM_MAPPING = {
    'language': 'language',
    'slugline': 'categorySupAnsa',
    'headline': 'title_B',
    'description_text': 'description_B',
    'sign_off': 'signOff',
    'byline': 'contentBy',
    'copyrightholder': 'copyrightHolder',
    'copyrightnotice': 'copyrightNotice',
    'usageterms': 'usageTerms',
    'pubstatus': 'status',
}

EXTRA_MAPPING = {
    'city': 'city',
    'nation': 'ctrName',
    'digitator': 'digitator',
    'coauthor': 'signature',
    'DateCreated': 'dateCreated',
    'DateRelease': 'releaseDate',
}


def format_date(datetime):
    return get_date(datetime).strftime(EXIF_DATETIME_FORMAT)


def apply_mapping(mapping, src, dest):
    if not src:
        return
    for src_key, dest_key in mapping.items():
        if src.get(src_key):
            dest[dest_key] = src[src_key]


def update_iptc_metadata(sender, item, **kwargs):
    if not hasattr(app.media, 'put_metadata'):
        # only works with vfs storage
        return

    if item.get('type') != 'picture':
        return

    if not request and not app.config['AUTO_PUBLISH_UPDATE_IPTC']:
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
    metadata['pubDate_N'] = format_date(firstcreated)

    if not metadata.get('dateCreated') and item.get('firstcreated'):
        metadata['dateCreated'] = format_date(item['firstcreated'])

    if not metadata.get('releaseDate') and item.get('versioncreated'):
        metadata['releaseDate'] = format_date(item['versioncreated'])

    if metadata.get('status') and 'stat:' not in metadata['status']:
        metadata['status'] = 'stat:{}'.format(metadata['status'])

    for _ in range(0, 3):
        try:
            original['media'] = app.media.put_metadata(original['media'], metadata)
            original['href'] = app.media.url_for_media(original['media'])
            break
        except VFSError:
            time.sleep(0.5)


def init_app(_app):
    superdesk.item_publish.connect(update_iptc_metadata)
