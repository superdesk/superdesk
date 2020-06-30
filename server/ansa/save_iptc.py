
import time
import superdesk
import logging

from flask import current_app as app, request
from datetime import datetime
from arrow.parser import ParserError
from superdesk.utc import utcnow, get_date
from ansa.constants import PHOTO_CATEGORIES_ID, PRODUCTS_ID, ANSA_DATETIME_FORMAT, EXIF_DATETIME_FORMAT
from ansa.vfs import VFSError


logger = logging.getLogger(__name__)

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
    'uri': 'originalTransmissionRef',
}

EXTRA_MAPPING = {
    'city': 'city',
    'nation': 'ctrName',
    'digitator': 'digitator',
    'coauthor': 'signature',
    'DateCreated': 'dateCreated',
    'DateRelease': 'releaseDate',
    'supplier': 'supplier',
}


def format_date(datetime_string):
    parsed = None
    if isinstance(datetime_string, datetime):
        parsed = datetime_string
    else:
        mixed = '{}T{}'.format(
            ANSA_DATETIME_FORMAT.split('T')[0],
            EXIF_DATETIME_FORMAT.split('T')[1],
        )
        formats = [
            ANSA_DATETIME_FORMAT,
            ANSA_DATETIME_FORMAT.replace('%z', ''),
            EXIF_DATETIME_FORMAT,
            EXIF_DATETIME_FORMAT.replace('%z', ''),
            mixed,
            mixed.replace('%z', ''),
        ]
        for format_ in formats:
            try:
                parsed = datetime.strptime(datetime_string, format_)
                break
            except ValueError:
                continue
        if not parsed:
            try:
                parsed = get_date(datetime_string)
            except ParserError:
                pass
    if parsed:
        formatted = parsed.isoformat()
        if '+' not in formatted:
            return '{}+00:00'.format(formatted)
        else:
            return formatted
    return datetime_string


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

    if not request and not app.config.get('AUTO_PUBLISH_UPDATE_IPTC'):
        return

    if item.get('type') == 'picture':
        update_image_metadata(item)
    elif item.get('associations'):
        for assoc in item['associations'].values():
            if assoc and assoc.get('type') == 'picture' and assoc.get('renditions'):
                update_image_metadata(item)


def update_image_metadata(item):
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
    elif metadata.get('dateCreated'):
        metadata['dateCreated'] = format_date(metadata['dateCreated'])

    if not metadata.get('releaseDate') and item.get('versioncreated'):
        metadata['releaseDate'] = format_date(item['versioncreated'])
    elif metadata.get('releaseDate'):
        metadata['releaseDate'] = format_date(metadata['releaseDate'])

    if metadata.get('status') and 'stat:' not in metadata['status']:
        metadata['status'] = 'stat:{}'.format(metadata['status'])

    media = original['media']
    for _ in range(0, 3):
        try:
            original['media'] = app.media.put_metadata(original['media'], metadata)
            original['href'] = app.media.url_for_media(original['media'])
            return
        except VFSError:
            logger.error('error when updating metadata for media', extra={'media': media})
            time.sleep(1)
    logger.error('no luck updating metadata for media', extra={'media': media})


def init_app(_app):
    superdesk.item_publish.connect(update_iptc_metadata)
