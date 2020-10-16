import re
import math
import arrow
import requests
import superdesk

from urllib.parse import urljoin
from flask import current_app as app
from superdesk.io.commands.update_ingest import update_renditions
from datetime import timedelta, datetime
from superdesk.utc import utcnow, utc_to_local
from superdesk.utils import ListCursor
from superdesk.timer import timer
from datetime import timedelta
from .constants import PHOTO_CATEGORIES_ID, EXIF_DATETIME_FORMAT, PRODUCTS_ID


SEARCH_ENDPOINT = 'ricerca.json'
DETAIL_ENDPOINT = 'detail.json'
ORIGINAL_ENDPOINT = 'binary/{}.jpg?guid={}&username={}&password={}'

THUMB_HREF = (
    'https://ansafoto.ansa.it/portaleimmagini/bdmproxy/{}.jpg?format=thumb&guid={}'
)
VIEWIMG_HREF = (
    'https://ansafoto.ansa.it/portaleimmagini/bdmproxy/{}.jpg?format=med&guid={}'
)

TIMEOUT = (5, 25)


def get_meta(doc, field, multi=False):
    try:
        if not multi:
            return doc['metadataMap'][field]['fieldValues'][0]['value']
        else:
            return [v['value'] for v in doc['metadataMap'][field]['fieldValues']]
    except KeyError:
        return None


def ansa_photo_api(endpoint):
    return urljoin(app.config['ANSA_PHOTO_API'], endpoint)


def extract_params(query, names):
    if isinstance(names, str):
        names = [names]
    findall = re.findall(r'([\w]+):\(([-\w\s*]+)\)', query)
    params = {}
    for name, _value in findall:
        value = _value.replace('-', r'\-')
        if name in names:
            if (
                params.get(name)
                and isinstance(params[name], str)
                and name == 'category'
            ):
                params[name] = [params[name], value]
            elif params.get(name) and name == 'category':
                params[name].append(value)
            else:
                params[name] = value  # last one wins
            query = query.replace('%s:(%s)' % (name, value), '')
    query = query.strip()
    if query:
        params['q'] = query
    return params


def fetch_metadata(item, doc):
    photo_category = get_meta(doc, 'categoryAnsa')
    if photo_category:
        photo_cat = superdesk.get_resource_service('vocabularies').find_one(
            req=None, _id=PHOTO_CATEGORIES_ID
        )
        if photo_cat:
            for subj in photo_cat.get('items', []):
                if subj.get('name') == photo_category:
                    item.setdefault('subject', []).append(
                        {
                            'name': subj['name'],
                            'qcode': subj.get('qcode'),
                            'scheme': PHOTO_CATEGORIES_ID,
                        }
                    )

    api_products = get_meta(doc, 'product', multi=True)
    if api_products:
        products_cv = superdesk.get_resource_service('vocabularies').find_one(
            req=None, _id=PRODUCTS_ID
        )
        if products_cv:
            for product in products_cv.get('items', []):
                if product.get('qcode') and product.get('qcode') in api_products:
                    item.setdefault('subject', []).append(
                        {
                            'name': product['name'],
                            'qcode': product['qcode'],
                            'scheme': PRODUCTS_ID,
                        }
                    )


FILTERS = [
    'title',
    'text',
    'place',
    'author',
    'creditline',
    'subcategory',
    'category',
    'orientation',
    'language',
    'datefrom',
]

QUERY_FILTERS = {
    'title': 'TITLE.k',
    'text': 'BODY.k',
    'place': 'PLACE.k',
    'author': 'AUTHOR.k',
    'creditline': 'CREDITLINE.k',
    'subcategory': 'SUBCAT.k',
}


QUERY_PARAMS = {
    'orientation': 'orientamento',
    'language': 'domainlang',
    'datefrom': 'datafrom',
}

TZ = 'Europe/Rome'
DATE_FORMAT = '%d/%m/%Y'
DATE_RANGES = {
    'today': lambda: local_date(timedelta(hours=0)),
    'week': lambda: local_date(-timedelta(days=7)),
    'month': lambda: local_date(-timedelta(days=30)),
    'year': lambda: utc_to_local(TZ, utcnow())
    .replace(day=1, month=1)
    .strftime(DATE_FORMAT),
}


def local_date(delta):
    now = utcnow()
    return utc_to_local(TZ, now + delta).strftime(DATE_FORMAT)


def set_default_search_operator(params):
    if (
        params.get('searchtext')
        and 'OR' not in params['searchtext']
        and 'AND' not in params['searchtext']
    ):
        groups = re.split(r'(\w+|".*?")', params['searchtext'])
        params['searchtext'] = ' AND '.join(
            [group for group in groups if bool(group) and group.strip()]
        )


class AnsaListCursor(ListCursor):
    def __init__(self, docs, count):
        super().__init__(docs)
        self._count = count

    def __len__(self):
        return len(self.docs)

    def count(self, **kwargs):
        return self._count


class AnsaPictureProvider(superdesk.SearchProvider):

    label = 'ANSA Pictures'

    @property
    def sess(self):
        if not hasattr(self, '_sess'):
            self._sess = requests.Session()
            self._sess.get(
                ansa_photo_api('/portaleimmagini/'), timeout=TIMEOUT
            )  # get cookies
        return self._sess

    def find(self, query):

        size = int(query.get('size', 25))
        page = math.ceil((int(query.get('from', 0)) + 1) / size)

        params = {
            'username': self.provider['config']['username'],
            'password': self.provider['config']['password'],
            'pgnum': page,
            'pgsize': size,
            'querylang': 'ITA',
            'order': 'desc',
            'changets': 'true',
        }

        query_string = (
            query.get('query', {})
            .get('filtered', {})
            .get('query', {})
            .get('query_string', {})
        )
        if query_string.get('query'):
            searchtext = query_string['query']
            filters = extract_params(searchtext, FILTERS)
            if filters.get('q'):
                params['searchtext'] = filters['q']
            query_filters = []
            for (key, val) in filters.items():
                if key in QUERY_FILTERS:
                    query_filters.append('%s = %s' % (QUERY_FILTERS[key], val.lower()))
                elif key == 'category':
                    values = [val] if isinstance(val, str) else val
                    for cat in values:
                        query_filters.append('categoryAnsa = %s' % cat)
                elif key in QUERY_PARAMS:
                    params[QUERY_PARAMS[key]] = val
                    if key == 'orientation':
                        params[QUERY_PARAMS[key]] = (
                            '1' if val.lower() == 'vertical' else '0'
                        )
                    if key == 'datefrom':
                        params[QUERY_PARAMS[key]] = DATE_RANGES[val.lower()]()
            if query_filters:
                params['filters'] = query_filters

        if not params.get('searchtext') and not params.get('filters'):
            return []  # avoid search with no filtering

        try:
            filters = query['query']['filtered']['filter']['and']
            for _filter in filters:
                try:
                    products = _filter['terms']['subject.qcode']
                    if products:
                        for product in products:
                            params.setdefault('filters', []).append(
                                'product = {}'.format(product)
                            )
                except KeyError:
                    continue
        except KeyError:
            pass

        set_default_search_operator(params)
        response = self.sess.get(
            ansa_photo_api(SEARCH_ENDPOINT), params=params, timeout=TIMEOUT
        )
        return self._parse_items(response)

    def _parse_items(self, response, fetch=False):
        if not response.status_code == requests.codes.ok:
            response.raise_for_status()

        items = []
        json_data = response.json()
        documents = json_data.get('renderResult', {}).get('documents', [])
        for doc in documents:
            md5 = get_meta(doc, 'orientationMD5')
            guid = get_meta(doc, 'idAnsa')
            pubdate_str = get_meta(doc, 'pubDate_N')
            try:
                pubdate = arrow.get(pubdate_str).datetime
            except ValueError:
                try:
                    pubdate = datetime.strptime(pubdate_str, EXIF_DATETIME_FORMAT)
                except ValueError:
                    continue
            try:
                signoff = get_meta(doc, 'contentBy').split('/')[1].strip()
            except (AttributeError, KeyError, IndexError):
                signoff = get_meta(doc, 'authorCode')
            item = {
                'type': 'picture',
                'pubstatus': get_meta(doc, 'status').replace('stat:', ''),
                '_id': guid,
                'guid': guid,
                'language': get_meta(doc, 'language') or 'it',
                'headline': get_meta(doc, 'title_B'),
                'slugline': get_meta(doc, 'categorySupAnsa'),
                'description_text': get_meta(doc, 'description_B'),
                'byline': get_meta(doc, 'contentBy'),
                'sign_off': signoff,
                'firstcreated': pubdate,
                'versioncreated': pubdate,
                'creditline': get_meta(doc, 'creditline'),
                'source': get_meta(doc, 'creditline'),
                'renditions': {
                    'thumbnail': {
                        'href': VIEWIMG_HREF.format(md5, guid),
                        'mimetype': 'image/jpeg',
                        'height': 256,
                        'width': 384,
                    },
                    'viewImage': {
                        'href': VIEWIMG_HREF.format(md5, guid),
                        'mimetype': 'image/jpeg',
                        'height': 256,
                        'width': 384,
                    },
                    'baseImage': {
                        'href': ansa_photo_api(ORIGINAL_ENDPOINT).format(
                            md5,
                            guid,
                            self.provider['config']['username'],
                            self.provider['config']['password'],
                        ),
                        'mimetype': 'image/jpeg',
                    },
                    'original': {
                        'href': ansa_photo_api(ORIGINAL_ENDPOINT).format(
                            md5,
                            guid,
                            self.provider['config']['username'],
                            self.provider['config']['password'],
                        ),
                        'mimetype': 'image/jpeg',
                    },
                },
                'place': [
                    {'name': get_meta(doc, 'city')},
                    {'name': get_meta(doc, 'ctrName')},
                ],
                'extra': {
                    'ansaid': guid,
                    'city': get_meta(doc, 'city'),
                    'nation': get_meta(doc, 'ctrName'),
                    'supplier': 'ANSA',
                    'coauthor': get_meta(doc, 'authorCode'),
                },
                'usageterms': get_meta(doc, 'usageTerms'),
                'copyrightholder': get_meta(doc, 'copyrightHolder')
                or get_meta(doc, 'copyright')
                or get_meta(doc, 'creditline'),
                'copyrightnotice': get_meta(doc, 'copyrightNotice'),
            }

            if get_meta(doc, 'releaseDate'):
                item['extra']['DateRelease'] = get_meta(doc, 'releaseDate')

            if get_meta(doc, 'dateCreated'):
                item['extra']['DateCreated'] = get_meta(doc, 'dateCreated')

            if fetch:
                fetch_metadata(item, doc)
            else:
                item['_fetchable'] = True

            items.append(item)

        # get used status from fetched items
        uris = [item['guid'] for item in items]
        if not fetch and uris:
            with timer('used'):
                fetched_items = list(
                    superdesk.get_resource_service('archive').search(
                        {
                            'query': {
                                'bool': {
                                    'filter': [
                                        {'terms': {'uri': uris}},
                                        {'term': {'used': True}},
                                    ]
                                }
                            }
                        }
                    )
                )
                for fetched in fetched_items:
                    item = next(
                        (item for item in items if item['guid'] == fetched['uri'])
                    )
                    item['used'] = True
                    item.setdefault('used_count', 0)
                    item['used_count'] += fetched.get("used_count", 0)
                    if fetched.get('used_updated') and (
                        not item.get('used_updated')
                        or item['used_updated'] < fetched['used_updated']
                    ):
                        item['used_updated'] = fetched['used_updated']

        return AnsaListCursor(
            items,
            json_data.get('simpleSearchResult', {}).get('totalResults', len(items)),
        )

    def fetch(self, guid):
        params = {
            'idAnsa': guid,
            'username': self.provider['config']['username'],
            'password': self.provider['config']['password'],
            'changets': 'true',
        }

        response = self.sess.get(
            ansa_photo_api(DETAIL_ENDPOINT), params=params, timeout=TIMEOUT
        )
        items = self._parse_items(response, fetch=True)
        item = items[0]

        # generate renditions
        original = item.get('renditions', {}).get('original', {})
        if original:
            update_renditions(item, original.get('href'), {})

        # it's in superdesk now, so make it ignore the api
        item['fetch_endpoint'] = ''
        return item

    def fetch_file(self, href, rendition, item):
        return app.media.get(rendition.get('media'))


def init_app(app):
    superdesk.register_search_provider('ansa', provider_class=AnsaPictureProvider)
