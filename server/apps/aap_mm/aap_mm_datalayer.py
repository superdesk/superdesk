from eve.io.base import DataLayer
from io import BytesIO
import urllib3
import json
import datetime
from superdesk.metadata.item import ITEM_TYPE, CONTENT_TYPE
from superdesk.utc import utc, utcnow
from eve_elastic.elastic import ElasticCursor
from superdesk.media.media_operations import process_file_from_stream, decode_metadata
from superdesk.media.renditions import generate_renditions, delete_file_on_error
from superdesk.errors import SuperdeskApiError
from superdesk.io.iptc import subject_codes
from flask import url_for
import urllib

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

        self._headers = {'cookie': r.getheader('set-cookie'), 'Content-Type': 'application/json'}

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
        """
        Called to execute a search against the AAP Mulitmedia API. It attempts to translate the search request
        passed in req to a suitable form for a search request against the API. It parses the response into a
        suitable ElasticCursor, the front end will never know.
        :param resource:
        :param req:
        :param lookup:
        :return:
        """
        if self._headers is None:
            self.__set_auth_cookie(self._app)

        url = self._app.config['AAP_MM_SEARCH_URL'] + '/Assets/search'
        query_keywords = '*:*'
        if 'query' in req['query']['filtered']:
            query_keywords = req['query']['filtered']['query']['query_string']['query']
            query_keywords = query_keywords.replace('slugline:', 'objectname:')
            query_keywords = query_keywords.replace('description:', 'captionabstract:')

        fields = {}
        for criterion in req.get('post_filter', {}).get('and', {}):
            # parse out the date range if possible
            if 'range' in criterion:
                start = None
                end = None
                daterange = None
                if 'firstcreated' in criterion.get('range', {}):
                    if 'gte' in criterion['range']['firstcreated']:
                        start = criterion['range']['firstcreated']['gte'][0:10]
                    if 'lte' in criterion['range']['firstcreated']:
                        end = criterion['range']['firstcreated']['lte'][0:10]
                # if there is a special start and no end it's one of the date buttons
                if start and not end:
                    if start == 'now-24H':
                        daterange = {'Dates': ['[NOW/HOUR-24HOURS TO NOW/HOUR]']}
                    if start == 'now-1w':
                        daterange = {'Dates': ['[NOW/DAY-7DAYS TO NOW/DAY]']}
                    if start == 'now-1M':
                        daterange = {'Dates': ['[NOW/DAY-1MONTH TO NOW/DAY]']}
                # we've got something but no daterange set above
                if (start or end) and not daterange:
                    daterange = {'DateRange': [{'Start': start, 'End': end}], 'DateCreatedFilter': 'true'}
                if daterange:
                    fields.update(daterange)

            if 'terms' in criterion:
                if 'type' in criterion.get('terms', {}):
                    fields.update({'MediaTypes': criterion['terms']['type']})
                if 'credit' in criterion.get('terms', {}):
                    fields.update({'Credits': criterion['terms']['credit']})
                if 'anpa_category.name' in criterion.get('terms', {}):
                    cat_list = []
                    for cat in criterion['terms']['anpa_category.name']:
                        qcode = [key for key, value in subject_codes.items() if value == cat]
                        if qcode:
                            for code in qcode:
                                cat_list.append(code)
                        else:
                            cat_list.append(cat)
                    fields.update({'Categories': cat_list})

        size = int(req.get('size', '25')) if int(req.get('size', '25')) > 0 else 25
        query = {'Query': query_keywords, 'pageSize': str(size),
                 'pageNumber': str(int(req.get('from', '0')) // size + 1)}

        r = self._http.urlopen('POST', url + '?' + urllib.parse.urlencode(query),
                               body=json.dumps(fields), headers=self._headers)
        hits = self._parse_hits(json.loads(r.data.decode('UTF-8')))
        return ElasticCursor(docs=hits['docs'], hits={'hits': hits, 'aggregations': self._parse_aggregations(hits)})

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
            new_doc[ITEM_TYPE] = CONTENT_TYPE.VIDEO
            purl = '{}?assetType=VIDEO&'.format(self._app.config['AAP_MM_CDN_URL'])
            purl += 'path=/rest/aap/archives/imagearc/dossiers/{}'.format(doc['AssetId'])
            purl += '/files/ipod&assetId={}&mimeType=video/mp4&dummy.mp4'.format(doc['AssetId'])
            new_doc['renditions'] = {'original': {'href': purl, 'mimetype': 'video/mp4'}}
        else:
            new_doc[ITEM_TYPE] = CONTENT_TYPE.PICTURE
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

    def _parse_aggregation(self, aggregations, facet, aggregation, hits):
        """
        Converts the "facet" to the "aggregate" based on the FacetResults in hits returns the equivalent
        aggregation in aggregations
        :param aggregations:
        :param facet:
        :param aggregation:
        :param hits:
        :return:
        """
        if 'FacetResults' in hits and facet in hits.get('FacetResults', {}):
            buckets = []
            name_set = set()
            for cat in hits.get('FacetResults', {}).get(facet, {}):
                if cat['DisplayName'] in name_set:
                    buckets.append({'doc_count': cat['Count'], 'key': cat['DisplayName'] + '/' + cat['Name'],
                                    'qcode': cat['Name']})
                else:
                    buckets.append({'doc_count': cat['Count'], 'key': cat['DisplayName'], 'qcode': cat['Name']})
                    name_set.add(cat['DisplayName'])
            aggregations[aggregation] = {'buckets': buckets}

    def _parse_aggregation_dates(self, aggregations, hits):
        """
        Extract the date related facets and convert into aggregations
        :param aggregations:
        :param hits:
        :return:
        """
        if 'FacetResults' in hits and 'Dates' in hits.get('FacetResults', {}):
            for date in hits.get('FacetResults', {}).get('Dates', {}):
                if date['Name'] == '[NOW/HOUR-24HOURS TO NOW/HOUR]':
                    aggregations['day'] = {'buckets': [{'doc_count': date['Count'], 'key': date['Name']}]}
                if date['Name'] == '[NOW/DAY-7DAYS TO NOW/DAY]':
                    aggregations['week'] = {'buckets': [{'doc_count': date['Count'], 'key': date['Name']}]}
                if date['Name'] == '[NOW/DAY-1MONTH TO NOW/DAY]':
                    aggregations['month'] = {'buckets': [{'doc_count': date['Count'], 'key': date['Name']}]}

    def _parse_aggregations(self, hits):
        """
        Given the hits returned from the AAP Mulitmedia API it will convert them to the same format as the
        Aggregations returned from the superdesk search against Elastic
        :param hits:
        :return: The converted aggregations
        """
        aggregations = {}
        self._parse_aggregation(aggregations, 'Categories', 'category', hits)
        self._parse_aggregation(aggregations, 'MediaTypes', 'type', hits)
        self._parse_aggregation(aggregations, 'Credits', 'credit', hits)
        self._parse_aggregation_dates(aggregations, hits)
        hits.pop('FacetResults')
        return aggregations

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
            if doc[ITEM_TYPE] == CONTENT_TYPE.PICTURE:
                if any(i['Name'] == 'Original' for i in resolutions['Image']):
                    url = self._app.config['AAP_MM_SEARCH_URL'] + '/Assets/{}/Original/download'.format(_id)
                    mime_type = 'image/jpeg'
                else:
                    raise FileNotFoundError
            elif doc[ITEM_TYPE] == CONTENT_TYPE.VIDEO:
                if any(v['Name'] == 'Ipod' for v in resolutions['Video']):
                    url = self._app.config['AAP_MM_SEARCH_URL'] + '/Assets/{}/Ipod/download'.format(_id)
                    mime_type = doc.get('renditions').get('original').get('mimetype')
                else:
                    raise FileNotFoundError
            else:
                raise NotImplementedError
        else:
            if doc[ITEM_TYPE] == CONTENT_TYPE.VIDEO:
                mime_type = doc.get('renditions').get('original').get('mimetype')
            else:
                mime_type = 'image/jpeg'
            url = doc['renditions']['original']['href']

        r = self._http.request('GET', url, headers=self._headers)
        out = BytesIO(r.data)
        file_name, content_type, metadata = process_file_from_stream(out, mime_type)

        inserted = []

        try:
            logger.debug('Going to save media file with %s ' % file_name)
            out.seek(0)
            file_id = self._app.media.put(out, filename=file_name, content_type=content_type, metadata=None)
            doc['mimetype'] = content_type
            doc['filemeta'] = decode_metadata(metadata)
            # set the version created to now to bring it to the top of the desk, images can be quite old
            doc['versioncreated'] = utcnow()
            inserted = [file_id]
            file_type = content_type.split('/')[0]
            rendition_spec = self._app.config['RENDITIONS']['picture']

            renditions = generate_renditions(out, file_id, inserted, file_type,
                                             content_type, rendition_spec,
                                             self.url_for_media, insert_metadata=False)
            doc['renditions'] = renditions
        except Exception as io:
            logger.exception(io)
            for file_id in inserted:
                delete_file_on_error(doc, file_id)

            raise SuperdeskApiError.internalError('Generating renditions failed')

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
