from eve.io.base import DataLayer
from io import BytesIO
import urllib3
import json
import datetime
from superdesk.utc import utc, utcnow
from eve_elastic.elastic import ElasticCursor
from superdesk.media.media_operations import process_file_from_stream, decode_metadata
from superdesk.media.renditions import generate_renditions, delete_file_on_error
from flask import url_for

import logging


urllib3.disable_warnings()

logger = logging.getLogger(__name__)


class AAPMMDatalayer(DataLayer):
    def __set_auth_cookie(self, app):
        if self._username is not None and self._password is not None:
            url = app.config['AAP_MM_SEARCH_URL'] + '/Users/login'
            values = {'username': self._username, 'password': self._password}
            r = self._http.urlopen('POST', url, headers={'Content-Type': 'application/json'}, body=json.dumps(values))
        else:
            url = app.config['AAP_MM_SEARCH_URL'] + '/Users/AnonymousToken'
            r = self._http.request('GET', url, redirect=False)

        self._headers = {'cookie': r.getheader('set-cookie')}

    def set_credentials(self, user, password):
        if user != self._username and user != '' and password != self._password and password != '':
            self._username = user
            self._password = password
            self.__set_auth_cookie(self._app)

    def init_app(self, app):
        app.config.setdefault('AAP_MM_SEARCH_URL', 'https://one-api.aap.com.au/api/v3')
        app.config.setdefault('AAP_MM_CDN_URL', 'http://one-cdn.aap.com.au/Preview.mp4')
        self._app = app
        self._headers = None
        self._username = None
        self._password = None
        self._http = urllib3.PoolManager()

    def find(self, resource, req, lookup):
        if self._headers is None:
            self.__set_auth_cookie(self._app)

        url = self._app.config['AAP_MM_SEARCH_URL'] + '/Assets/search'
        query_keywords = '*:*'
        if 'query' in req['query']['filtered']:
            query_keywords = req['query']['filtered']['query']['query_string']['query']
        fields = {'query': query_keywords, 'pageSize': str(req.get('size', '25')),
                  'pageNumber': str(int(req.get('from', '0')) // int(req.get('size', '25')) + 1)}
        r = self._http.request('GET', url, fields=fields, headers=self._headers)
        hits = self._parse_hits(json.loads(r.data.decode('UTF-8')))
        return ElasticCursor(docs=hits['docs'], hits={'hits': hits})

    def _parse_doc(self, doc):
        new_doc = {}
        new_doc['_id'] = doc['AssetId']
        new_doc['guid'] = doc['AssetId']
        new_doc['headline'] = doc['Title']
        new_doc['description'] = doc['Description']
        new_doc['source'] = doc['Credit']
        if 'Source' in doc:
            new_doc['original_source'] = doc['Credit'] + '/' + str(doc.get('Source', ''))
        else:
            new_doc['original_source'] = doc['Credit']
        new_doc['versioncreated'] = self._datetime(doc['ModifiedDate'])
        new_doc['firstcreated'] = self._datetime(doc['CreationDate'])
        new_doc['pubstatus'] = 'usable'
        # This must match the action
        new_doc['_type'] = 'externalsource'
        # entry that the client can use to identify the fetch endpoint
        new_doc['fetch_endpoint'] = 'aapmm'
        if doc['AssetType'] == 'VIDEO':
            new_doc['type'] = 'video'
            purl = '{}?assetType=VIDEO&'.format(self._app.config['AAP_MM_CDN_URL'])
            purl += 'path=/rest/aap/archives/imagearc/dossiers/{}'.format(doc['AssetId'])
            purl += '/files/ipod&assetId={}&mimeType=video/mp4&dummy.mp4'.format(doc['AssetId'])
            new_doc['renditions'] = {'original': {'href': purl, 'mimetype': 'video/mp4'}}
        else:
            new_doc['type'] = 'picture'
            new_doc['renditions'] = {
                'viewImage': {'href': doc.get('Preview', doc.get('Layout'))['Href']},
                'thumbnail': {'href': doc.get('Thumbnail', doc.get('Layout'))['Href']},
                'original': {'href': doc.get('Preview', doc.get('Layout'))['Href']},
                'baseImage': {'href': doc.get('Preview', doc.get('Layout'))['Href']},
            }

        new_doc['slugline'] = doc['Title']
        new_doc['byline'] = doc['Byline']
        new_doc['ednote'] = doc['SpecialInstructions']
        doc.clear()
        doc.update(new_doc)

    def _parse_hits(self, hits):
        hits['docs'] = hits.pop('Assets')
        hits['total'] = hits.pop('Total')
        for doc in hits['docs']:
            self._parse_doc(doc)
        return hits

    def _datetime(self, string):
        try:
            dt = datetime.datetime.strptime(string, '%Y-%m-%dT%H:%M:%S').replace(tzinfo=utc)
        except:
            dt = utcnow()
        return dt

    def _get_resolutions(self, id):
        url = self._app.config['AAP_MM_SEARCH_URL'] + '/Assets/Resolutions'
        values = [id]
        headers = dict(self._headers)
        headers['Content-Type'] = 'application/json'
        r = self._http.urlopen('POST', url, headers=headers, body=json.dumps(values))
        return json.loads(r.data.decode('UTF-8'))

    def find_all(self, resource, max_results=1000):
        raise NotImplementedError

    def find_one(self, resource, req, **lookup):
        raise NotImplementedError

    def find_one_raw(self, resource, _id):
        if self._headers is None:
            self.__set_auth_cookie(self._app)

        url = self._app.config['AAP_MM_SEARCH_URL'] + '/Assets/{}'.format(_id)
        r = self._http.request('GET', url, headers=self._headers)
        doc = json.loads(r.data.decode('UTF-8'))
        self._parse_doc(doc)
        if 'fetch_endpoint' in doc:
            del doc['fetch_endpoint']

        # Only if we have credentials can we download the original if the account has that privilege
        if self._username is not None and self._password is not None:
            resolutions = self._get_resolutions(_id)
            if doc['type'] == 'picture':
                if any(i['Name'] == 'Original' for i in resolutions['Image']):
                    url = self._app.config['AAP_MM_SEARCH_URL'] + '/Assets/{}/Original/download'.format(_id)
                    mime_type = 'image/jpeg'
                    source_ref = {'href': url, 'mimetype': mime_type}
                else:
                    raise FileNotFoundError
            elif doc['type'] == 'video':
                if any(v['Name'] == 'Ipod' for v in resolutions['Video']):
                    url = self._app.config['AAP_MM_SEARCH_URL'] + '/Assets/{}/Ipod/download'.format(_id)
                    mime_type = doc.get('renditions').get('original').get('mimetype')
                else:
                    raise FileNotFoundError
                if any(v['Name'] == 'Video' for v in resolutions['Video']):
                    source_ref = {
                        'href': self._app.config['AAP_MM_SEARCH_URL'] + '/Assets/{}/Video/download'.format(_id),
                        'mimetype': 'video/quicktime'}
                else:
                    raise FileNotFoundError
            else:
                raise NotImplementedError
        else:
            if doc['type'] == 'video':
                mime_type = doc.get('renditions').get('original').get('mimetype')
            else:
                mime_type = 'image/jpeg'
            url = doc['renditions']['original']['href']
            source_ref = {'href': url, 'mimetype': mime_type}

        r = self._http.request('GET', url, headers=self._headers)
        out = BytesIO(r.data)
        file_name, content_type, metadata = process_file_from_stream(out, mime_type)

        try:
            logger.debug('Going to save media file with %s ' % file_name)
            out.seek(0)
            file_id = self._app.media.put(out, filename=file_name, content_type=content_type, metadata=metadata)
            doc['mimetype'] = content_type
            doc['filemeta'] = decode_metadata(metadata)
            # set the version created to now to bring it to the top of the desk, images can be quite old
            doc['versioncreated'] = utcnow()
            inserted = [file_id]
            file_type = content_type.split('/')[0]
            rendition_spec = self._app.config['RENDITIONS']['picture']

            renditions = generate_renditions(out, file_id, inserted, file_type,
                                             content_type, rendition_spec, self.url_for_media)
            doc['renditions'] = renditions
            doc['renditions']['original_source'] = source_ref
        except Exception as io:
            logger.exception(io)
            for file_id in inserted:
                delete_file_on_error(doc, file_id)

        return doc

    def url_for_media(self, media_id):
        return url_for('upload_raw.get_upload_as_data_uri', media_id=media_id,
                       _external=True, _schema=self._app.config['URL_PROTOCOL'])

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
