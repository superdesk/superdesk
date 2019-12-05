
import os
import arrow

from flask import current_app as app
from datetime import datetime
from superdesk import get_resource_service
from superdesk.io.feed_parsers.image_iptc import ImageIPTCFeedParser, get_meta_iptc
from ansa.constants import PHOTO_CATEGORIES_ID, PRODUCTS_ID, EXIF_DATETIME_FORMAT
from superdesk.media.iim_codes import iim_codes

# parse extra codes
PRODUCT_ID_KEY = 'Product I.D.'

iim_codes[(1, 50)] = PRODUCT_ID_KEY

CORE_MAPPING = {
    'Object Name': 'slugline',
    'By-line': 'byline',
    'Credit': 'copyrightholder',
    'Copyright Notice': 'usageterms',
    'Language Identifier': 'language',
}

EXTRA_MAPPING = {
    'City': 'city',
    'Country/Primary Location Name': 'nation',
    'Writer/Editor': 'digitator',
    'By-line Title': 'coauthor',
    'Source': 'supplier',
}


def get_subject_refs(metadata):
    refs = metadata.get('Subject Reference')
    if not refs:
        return []
    return refs if isinstance(refs, list) else [refs]


def parse_datetime(date, time):
    _datetime = 'T'.join([date, time])
    try:
        return datetime.strptime(_datetime, EXIF_DATETIME_FORMAT)
    except ValueError:
        try:
            return arrow.get(_datetime).datetime
        except ValueError:
            return


class PictureParser(ImageIPTCFeedParser):
    """Use filename for guid."""

    @property
    def products(self):
        if not hasattr(self, '_products'):
            self._products = []
            products = get_resource_service('vocabularies').find_one(req=None, _id=PRODUCTS_ID)
            if products:
                self._products = products.get('items', [])
        return self._products

    @property
    def categories(self):
        if not hasattr(self, '_categories'):
            self._categories = []
            photo_cat = get_resource_service('vocabularies').find_one(req=None, _id=PHOTO_CATEGORIES_ID)
            if photo_cat:
                self._categories = photo_cat.get('items', [])
        return self._categories

    def parse_item(self, image_path):
        item = super().parse_item(image_path)

        item['guid'] = item['uri'] = os.path.basename(image_path)
        item['extra'] = {}
        item['subject'] = []

        # custom metadata parsing
        with open(image_path, mode='rb') as f:
            metadata = get_meta_iptc(f)

        for src, dest in CORE_MAPPING.items():
            if metadata.get(src):
                item[dest] = metadata[src]

        for src, dest in EXTRA_MAPPING.items():
            if metadata.get(src):
                item['extra'][dest] = metadata[src]

        refs = get_subject_refs(metadata)
        for subj in app.subjects.get_items():
            for ref in refs:
                if subj.get('qcode') and subj['qcode'] in ref:
                    item['subject'].append(subj)

        if metadata.get('Category'):
            for cat in self.categories:
                if cat.get('name') == metadata['Category']:
                    item['subject'].append({
                        'name': cat.get('name'),
                        'qcode': cat.get('qcode'),
                        'scheme': PHOTO_CATEGORIES_ID,
                    })

        if metadata.get(PRODUCT_ID_KEY):
            ids = metadata[PRODUCT_ID_KEY].split()
            for product in self.products:
                if product.get('qcode') in ids:
                    item['subject'].append({
                        'name': product.get('name'),
                        'qcode': product.get('qcode'),
                        'scheme': PRODUCTS_ID,
                    })

        if metadata.get('Date Created') and metadata.get('Time Created'):
            item['extra']['DateCreated'] = parse_datetime(metadata['Date Created'], metadata['Time Created'])

        if metadata.get('Release Date') and metadata.get('Release Time'):
            item['extra']['DateRelease'] = parse_datetime(metadata['Release Date'], metadata['Release Time'])

        return item
