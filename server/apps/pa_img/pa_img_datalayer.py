# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014, 2015 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import datetime
from io import BytesIO
import json
import logging
import re

from eve.io.base import DataLayer
from eve_elastic.elastic import ElasticCursor
from superdesk.upload import url_for_media
import urllib3

from superdesk.errors import SuperdeskApiError
from superdesk.media.media_operations import process_file_from_stream, decode_metadata, download_file_from_url
from superdesk.media.renditions import generate_renditions, delete_file_on_error
from superdesk.metadata.item import ITEM_TYPE, CONTENT_TYPE
from superdesk.utc import utc, utcnow


urllib3.disable_warnings()

logger = logging.getLogger(__name__)


def extract_params(query, names):
    findall = re.findall('([\w]+):\(([\w\s]+)\)', query)
    params = {name: value for (name, value) in findall if name in names}
    result = re.search('^\(([\w\s]+)\)', query)
    if result:
        params['text'] = result.group(1)
    else:
        result = re.search('[^:]+\(([\w\s]+)\)', query)
        if result:
            params['text'] = result.group(1)
    return params


def processLimits(offset, size):
    """
    Try to find a page index and a minimum page size so the requested interval to
    be included in only page. Max supported page size is 200.
    page_index * page_size <= offset
    offset + size < (page_index + 1) * page_size
    """
    maxSize = 200
    size = max(10, min(maxSize, size))

    for i in range(size, maxSize):
        page = offset // i
        if page * i <= offset and offset + size <= (page + 1) * i:
            return page + 1, i
    return offset // maxSize + 1, maxSize


class PaImgDatalayer(DataLayer):
    def set_credentials(self, user, password):
        self._token = user

    def init_app(self, app):
        app.config.setdefault('PAIMG_SEARCH_URL', 'https://images.api.press.net/api/v2')
        self._app = app
        self._token = None
        self._headers = {'Content-Type': 'application/json'}
        self._http = urllib3.PoolManager()

    def fetch_file(self, url):
        """Get file stream for given image url.

        It will fetch the file using predefined auth token.

        :param url: pa image api url
        """
        stream, name, mime = download_file_from_url('%s?token=%s' % (url, self._token))
        return stream

    def find(self, resource, req, lookup):
        """
        Called to execute a search against the PA Image API. It attempts to translate the search request
        passed in req to a suitable form for a search request against the API. It parses the response into a
        suitable ElasticCursor.
        :param resource:
        :param req:
        :param lookup:
        :return:
        """

        url = self._app.config['PAIMG_SEARCH_URL']
        fields = {}
        if 'query' in req['query']['filtered']:
            query_keywords = req['query']['filtered']['query']['query_string']['query'] \
                .replace('slugline:', 'keywords:') \
                .replace('description:', 'caption:')
            fields = extract_params(query_keywords, ['headline', 'caption', 'keywords'])

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
                        daterange = 1
                    if start == 'now-1w':
                        daterange = 7
                    if start == 'now-1M':
                        daterange = 31
                # we've got something but no daterange set above
                if (start or end) and not daterange:
                    if start:
                        fields['created_since'] = start
                    if end:
                        fields['created_before'] = end
                if daterange:
                    fields['days_since'] = daterange

            if 'terms' in criterion:
                if 'type' in criterion.get('terms', {}):
                    type = criterion['terms']['type']
                    if type == CONTENT_TYPE.PICTURE:
                        fields['photos'] = 'true'

        if not fields:
            url += '/latest'
            fields['ck'] = 'public'
            fields['days_since'] = 5
        else:
            url += '/search'
            fields['ck'] = 'superdesk'

        page, limit = processLimits(int(req.get('from', '0')), int(req.get('size', '25')))

        fields['page'] = page
        fields['limit'] = limit

        if self._token:
            fields['token'] = self._token

        r = self._http.request_encode_url('GET', url,
                                          fields=fields, headers=self._headers)
        hits = self._parse_hits(json.loads(r.data.decode('UTF-8')))
        return ElasticCursor(docs=hits['docs'], hits={'hits': hits})

    def _parse_doc(self, doc):
        new_doc = {}
        new_doc['_id'] = doc['urn']
        new_doc['guid'] = doc['urn']
        if 'headline' in doc:
            new_doc['headline'] = doc['headline']
        if 'description_text' in doc:
            new_doc['description'] = doc['description_text']
        if 'credit' in doc:
            new_doc['source'] = doc['credit']
            if 'original_reference' in doc:
                new_doc['original_source'] = doc['credit'] + '/' + str(doc.get('original_reference', ''))
            else:
                new_doc['original_source'] = doc['credit']
        new_doc['versioncreated'] = self._datetime(doc['versioncreated'])
        new_doc['firstcreated'] = self._datetime(doc['firstcreated'])
        new_doc['pubstatus'] = 'usable'
        # This must match the action
        new_doc['_type'] = 'externalsource'
        # entry that the client can use to identify the fetch endpoint
        new_doc['fetch_endpoint'] = 'paimg'
        if doc['type'] == 'picture':
            new_doc[ITEM_TYPE] = CONTENT_TYPE.PICTURE
            if 'renditions' in doc:
                renditions = doc.get('renditions')
                new_doc['renditions'] = {
                    'original': renditions.get('full'),
                    'thumbnail': renditions.get('thumbnail_lrg'),
                    'viewImage': renditions.get('sample'),
                }

        if 'byline' in doc:
            new_doc['byline'] = doc['byline']
        if 'keywords' in doc:
            new_doc['slugline'] = doc['keywords']
        if 'usageterms' in doc:
            new_doc['usageterms'] = doc['usageterms']
        doc.clear()
        doc.update(new_doc)

    def _parse_hits(self, hits):
        hits['docs'] = hits.pop('results')
        hits['total'] = hits.pop('totalresults')
        for doc in hits['docs']:
            self._parse_doc(doc)
        return hits

    def _datetime(self, string):
        try:
            dt = datetime.datetime.strptime(string, '%Y-%m-%dT%H:%M:%S').replace(tzinfo=utc)
        except:
            dt = utcnow()
        return dt

    def find_all(self, resource, max_results=1000):
        raise NotImplementedError

    def find_one(self, resource, req, **lookup):
        raise NotImplementedError

    def find_one_raw(self, resource, _id):
        fields = {}
        if self._token:
            fields['token'] = self._token

        url = self._app.config['PAIMG_SEARCH_URL'] + '/meta/{}'.format(_id)
        r = self._http.request_encode_url('GET', url, fields=fields, headers=self._headers)
        doc = json.loads(r.data.decode('UTF-8'))
        self._parse_doc(doc)

        if 'fetch_endpoint' in doc:
            del doc['fetch_endpoint']

        if doc[ITEM_TYPE] == CONTENT_TYPE.PICTURE:
            if 'original' in doc.get('renditions', {}):
                url = doc['renditions']['original']['href']
                mime_type = 'image/jpeg'
            else:
                raise FileNotFoundError
        else:
            raise NotImplementedError

        if not url or not doc['renditions']['original'].get('downloadable', False):
            raise SuperdeskApiError('original not downloadable', payload={'no_original': True})

        r = self._http.request_encode_url('GET', url, fields=fields, headers=self._headers)
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
                                             url_for_media, insert_metadata=False)
            doc['renditions'] = renditions
        except Exception as io:
            logger.exception(io)
            for file_id in inserted:
                delete_file_on_error(doc, file_id)

            raise SuperdeskApiError.internalError('Generating renditions failed')

        return doc

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
