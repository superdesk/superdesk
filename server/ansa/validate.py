
import superdesk

from enum import IntEnum
from superdesk.text_utils import get_char_count
from superdesk.signals import item_validate

MASK_FIELD = 'output_code'


class Validators(IntEnum):
    HEADLINE_REQUIRED = 0
    SHORTTITLE_REQUIRED = 1
    SUBTITLE_REQUIRED = 2
    SUBJECT_REQUIRED = 3
    BODY_LENGTH_512 = 4
    BODY_LENGTH_6400 = 5
    BODY_LENGTH_2224 = 6
    FEATURED_REQUIRED = 7
    GALLERY_REQUIRED = 8


def get_active_mask(products):
    mask = {}
    if products:
        cv = superdesk.get_resource_service('vocabularies').find_one(req=None, _id='products')
        codes = {product['qcode']: 1 for product in products}
        if cv and cv.get('items'):
            for item in cv['items']:
                if codes.get(item.get('qcode')) and item.get(MASK_FIELD) and len(str(item[MASK_FIELD])) == 9:
                    value = str(item[MASK_FIELD])
                    for i in range(9):
                        if value[i] == '1':
                            mask[i] = True
    return mask


def validate(sender, item, response, error_fields, **kwargs):
    products = [subject for subject in item.get('subject', []) if subject.get('scheme') == 'products']
    mask = get_active_mask(products)
    extra = item.get('extra', {})
    length = get_char_count(item.get('body_html') or '<p></p>')

    if mask.get(Validators.HEADLINE_REQUIRED):
        if not item.get('headline'):
            response.append('Headline is required')

    if mask.get(Validators.SHORTTITLE_REQUIRED):
        if not extra.get('shorttitle'):
            response.append('Short Title is required')

    if mask.get(Validators.SUBTITLE_REQUIRED):
        if not extra.get('subtitle'):
            response.append('Subtitle is required')

    if mask.get(Validators.SUBJECT_REQUIRED):
        subjects = [subject for subject in item.get('subject', []) if subject.get('scheme') is None]
        if not len(subjects):
            response.append('Subject is required')

    if mask.get(Validators.BODY_LENGTH_512) and length > 512:
        response.append('Body is longer than 512 characters')
    elif mask.get(Validators.BODY_LENGTH_2224) and length > 2224:
        response.append('Body is longer than 2224 characters')
    elif mask.get(Validators.BODY_LENGTH_6400) and length > 6400:
        response.append('Body is longer than 6400 characters')

    if mask.get(Validators.FEATURED_REQUIRED):
        if not item.get('associations') or not item['associations'].get('featuremedia'):
            response.append('Featured photo is required')

    if mask.get(Validators.GALLERY_REQUIRED):
        if not item.get('photoGallery'):
            response.append('Photo gallery is required')


def init_app(app):
    item_validate.connect(validate)
