
import json
import math
import arrow
import logging
import requests
import superdesk


SEARCH_URL = 'http://172.20.14.88/ansafoto/portaleimmagini/api/ricerca.json'
SEARCH_USERNAME = 'user1'
SEARCH_PASSWORD = 'pwd1'

THUMB_HREF = 'https://ansafoto.ansa.it/portaleimmagini/bdmproxy/{}.jpg?format=thumb'
VIEWIMG_HREF = 'https://ansafoto.ansa.it/portaleimmagini/bdmproxy/{}.jpg?format=med'

logger = logging.getLogger('superdesk')


def get_meta(doc, field):
    try:
        return doc['metadataMap'][field]['fieldValues'][0]['value']
    except KeyError:
        return None


class AnsaPictureProvider(superdesk.SearchProvider):

    label = 'ANSA Pictures'

    def find(self, query):

        size = int(query.get('size', 25))
        page = math.ceil((int(query.get('from', 0)) + 1) / size)

        params = {
            'username': SEARCH_USERNAME,
            'password': SEARCH_PASSWORD,
            'pgnum': page,
            'pgsize': size,
            'querylang': 'ITA',
            'order': 'desc',
        }

        query_string = query.get('query', {}).get('filtered', {}).get('query', {}).get('query_string', {})
        if query_string.get('query'):
            params['searchtext'] = query_string.get('query').replace('(', '').replace(')', '')

        logger.info('search %s %s', query, params)

        response = requests.get(SEARCH_URL, params=params, timeout=(5, 25))
        if not response.status_code == requests.codes.ok:
            response.raise_for_status()

        items = []
        json_data = response.json()
        documents = json_data.get('renderResult', {}).get('documents', [])
        for doc in documents:
            md5 = get_meta(doc, 'orientationMD5')
            pubdate = arrow.get(get_meta(doc, 'pubDate_N'), 'YYYYMMDDHHmmss').datetime
            items.append({
                'type': 'picture',
                'pubstatus': get_meta(doc, 'status').replace('stat:', ''),
                '_id': get_meta(doc, 'idAnsa'),
                'guid': get_meta(doc, 'idAnsa'),
                'headline': get_meta(doc, 'title_B'),
                'description_text': get_meta(doc, 'description_B'),
                'byline': get_meta(doc, 'contentBy'),
                'firstcreated': pubdate,
                'versioncreated': pubdate,
                'creditline': get_meta(doc, 'creditline'),
                'source': get_meta(doc, 'creditline'),
                'renditions': {
                    'thumbnail': {
                        'href': VIEWIMG_HREF.format(md5),
                        'mimetype': 'image/jpeg',
                    },
                    'viewImage': {
                        'href': VIEWIMG_HREF.format(md5),
                        'mimetype': 'image/jpeg',
                    },
                    'baseImage': {
                        'href': VIEWIMG_HREF.format(md5),
                        'mimetype': 'image/jpeg',
                    },
                    'original': {
                        'href': VIEWIMG_HREF.format(md5),
                        'mimetype': 'image/jpeg',
                    },
                },
                'place': [
                    {'name': get_meta(doc, 'city')},
                    {'name': get_meta(doc, 'ctrName')},
                ],
            })
        return items


def init_app(app):
    superdesk.register_search_provider('ansa', provider_class=AnsaPictureProvider)
