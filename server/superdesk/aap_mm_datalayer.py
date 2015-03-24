from eve.io.base import DataLayer
import urllib3
import json
from eve_elastic.elastic import ElasticCursor

urllib3.disable_warnings()


class AAPMMDatalayer(DataLayer):

    def init_app(self, app):
        app.config.setdefault('AAP_MM_SEARCH_URL', 'https://one-api.aap.com.au/api/v3')
        self._app = app
        self._headers = None
        self._http = urllib3.PoolManager()
        if 'AAP_MM_USER' in app.config and 'AAP_MM_PASSWORD' in app.config:
            url = app.config['AAP_MM_SEARCH_URL'] + '/Users/login'
            values = {'username': app.config['AAP_MM_USER'], 'password': app.config['AAP_MM_PASSWORD']}
            r = self._http.urlopen('POST', url, headers={'Content-Type': 'application/json'}, body=json.dumps(values))
        else:
            url = app.config['AAP_MM_SEARCH_URL'] + '/Users/AnonymousToken'
            r = self._http.request('GET', url, redirect=False)
        self._headers = {'cookie': r.getheader('set-cookie')}

    def find(self, resource, req, lookup):
        url = self._app.config['AAP_MM_SEARCH_URL'] + '/Assets/search'
        query_keywords = '*:*'
        if 'query' in req['query']['filtered']:
            query_keywords = req['query']['filtered']['query']['query_string']['query']
        fields = {'query': query_keywords, 'pageSize': str(req['size']),
                  'pageNumber': str(int(req['from']) // int(req['size']) + 1)}
        r = self._http.request('GET', url, fields=fields, headers=self._headers)
        return json.loads(r.data.decode('UTF-8'))

    def _parse_hits(self, hits):
        hits['docs'] = hits.pop('Assets')
        hits['total'] = hits.pop('Total')
        for doc in hits['docs']:
            doc['_id'] = doc.pop('AssetId')
            doc['guid'] = doc['_id']
            doc['headline'] = doc.pop('Title')
            doc['body_html'] = doc.pop('Description')
            doc['description'] = doc['body_html']
            doc['source'] = doc['Credit']
            doc['original_source'] = doc.pop('Credit') + '/' + doc.pop('Source')
            doc['versioncreated'] = doc.pop('ModifiedDate')
            doc['firstcreated'] = doc.pop('CreationDate')
            doc['type'] = 'picture'
            doc['renditions'] = {'viewImage': {'href': doc['Layout']['Href']},
                                 'thumbnail': {'href': doc['Thumbnail']['Href']},
                                 'original': {'href': doc['Layout']['Href']},
                                 'baseImage': {'href': doc['Layout']['Href']}}
            if doc['AssetType'] == 'VIDEO':
                doc['type'] = 'video'
                # don't actually know!
                doc['mimetype'] = 'image/jpeg'
            else:
                doc['type'] = 'picture'
                doc['mimetype'] = 'image/jpeg'

            doc['slugline'] = doc.pop('Byline')
        return ElasticCursor(docs=hits['docs'], hits={'hits': hits})

    def find_all(self, resource, max_results=1000):
        raise NotImplementedError

    def find_one(self, resource, req, **lookup):
        raise NotImplementedError

    def find_one_raw(self, resource, _id):
        raise NotImplementedError

    def find_list_of_ids(self, resource, ids, client_projection=None):
        raise NotImplementedError

    def insert(self, resource, docs, **kwargs):
        raise NotImplementedError

    def update(self, resource, id_, updates, original):
        raise NotImplementedError

    def update_all(self, resource, query, updates):
        raise NotImplementedError

    def replace(self, resource, id_, document, original):
        raise NotImplementedError

    def remove(self, resource, lookup=None):
        raise NotImplementedError

    def is_empty(self, resource):
        raise NotImplementedError
