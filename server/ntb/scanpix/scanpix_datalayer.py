# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014, 2015, 2016 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import arrow
import logging
import re
import requests
import json
from os.path import splitext

from io import BytesIO
from eve.io.base import DataLayer
from eve_elastic.elastic import ElasticCursor
from superdesk.upload import url_for_media

from superdesk.errors import SuperdeskApiError, ProviderError
from superdesk.media.media_operations import process_file_from_stream, decode_metadata
from superdesk.media.renditions import generate_renditions, delete_file_on_error, get_renditions_spec
from superdesk.metadata.item import ITEM_TYPE, CONTENT_TYPE
from superdesk.utc import utcnow, get_date, local_to_utc
import mimetypes


# scanpix preview size to use (if available) for superdesk rendition
# preview sizes are in order of preference, first found is used
REND2PREV = {
    'thumbnail': ('generated_jpg', 'thumbnail', 'thumbnail_big'),
    'viewImage': ('preview', 'thumbnail_big', 'thumbnail', 'preview_big'),
    'baseImage': ('mp4_preview', 'mp4_thumbnail', 'preview_big', 'preview', 'thumbnail_big', 'thumbnail')}
logger = logging.getLogger('ntb:scanpix')

SCANPIX_TZ = 'Europe/Oslo'

def extract_params(query, names):
    if isinstance(names, str):
        names = [names]
    findall = re.findall('([\w]+):\(([-\w\s*]+)\)', query)
    params = {name: value for (name, value) in findall if name in names}
    for name, value in findall:
        query = query.replace('%s:(%s)' % (name, value), '')
    query = query.strip()
    # escape dashes
    for name, value in params.items():
        params[name] = value.replace('-', '\-')
    if query:
        params['q'] = query
    return params


class ScanpixDatalayer(DataLayer):
    def set_credentials(self, user, password):
        self._user = user
        self._password = password

    def init_app(self, app):
        app.config.setdefault('SCANPIX_SEARCH_URL', 'http://api.scanpix.no/v2')
        self._app = app
        self._user = None
        self._password = None
        self._headers = {
            'Content-Type': 'application/json',
        }

    def fetch_file(self, url):
        """Get file stream for given image url.

        It will fetch the file using predefined auth token.

        :param url: pa image api url
        """
        raise NotImplementedError

    def find(self, resource, req, lookup):
        """
        Called to execute a search against the Scanpix API. It attempts to translate the search request
        passed in req to a suitable form for a search request against the API. It parses the response into a
        suitable ElasticCursor.
        :param resource:
        :param req:
        :param lookup:
        :return:
        """
        url = self._app.config['SCANPIX_SEARCH_URL'] + '/search'
        data = {
            'mainGroup': 'any',
            'archived': {
                'max': '',
                'min': ''
            }
        }

        if 'query' in req['query']['filtered']:
            query = req['query']['filtered']['query']['query_string']['query'] \
                .replace('slugline:', 'keywords:') \
                .replace('description:', 'caption:')

            # Black & White
            try:
                bw = bool(int(extract_params(query, 'bw')['bw']))
            except KeyError:
                pass
            else:
                if bw:
                    data['saturation'] = {'max': 1}

            # Clear Edge
            try:
                clear_edge = bool(int(extract_params(query, 'clear_edge')['clear_edge']))
            except KeyError:
                pass
            else:
                if clear_edge:
                    data['clearEdge'] = True

            # subscription
            try:
                data['subscription'] = extract_params(query, 'subscription')['subscription']
            except KeyError:
                data['subscription'] = 'subscription'  # this is requested as a default value

            if 'ntbtema' in resource and data['subscription'] == 'subscription':
                # small hack for SDNTB-250
                data['subscription'] = 'punchcard'

            if data['subscription'] == 'all':
                del data['subscription']

            text_params = extract_params(query, ('headline', 'keywords', 'caption', 'text'))
            # combine all possible text params to use the q field.
            data['searchString'] = ' '.join(text_params.values())

            try:
                ids = extract_params(query, 'id')['id'].split()
            except KeyError:
                pass
            else:
                data['refPtrs'] = ids

        for criterion in req.get('post_filter', {}).get('and', {}):
            if 'range' in criterion:
                start = None
                end = None
                filter_data = criterion.get('range', {})

                if 'firstcreated' in filter_data:
                    created = criterion['range']['firstcreated']
                    if 'gte' in created:
                        start = created['gte'][0:10]
                    if 'lte' in created:
                        end = created['lte'][0:10]

                # if there is a special start and no end it's one of the date buttons
                if start and not end:
                    if start == 'now-24H':
                        data['timeLimit'] = 'last24 '
                    if start == 'now-1w':
                        data['timeLimit'] = 'lastweek '
                    if start == 'now-1M':
                        data['timeLimit'] = 'lastmonth '
                elif start or end:
                    if start:
                        data['archived']['min'] = start
                    if end:
                        data['archived']['max'] = end

            if 'terms' in criterion:
                if 'type' in criterion.get('terms', {}):
                    type_ = criterion['terms']['type']
                    if type_ == CONTENT_TYPE.VIDEO:
                        data['mainGroup'] = 'video'

        offset, limit = int(req.get('from', '0')), max(10, int(req.get('size', '25')))
        data['offset'] = offset
        data['showNumResults'] = limit
        r = self._request(url, data)
        hits = self._parse_hits(r.json())
        return ElasticCursor(docs=hits['docs'], hits={'hits': hits})

    def _request(self, url, data):
        """Perform GET request to given url.

        It adds predefined headers and auth token if available.

        :param url
        :param data
        """
        r = requests.post(url, data=json.dumps(data), headers=self._headers, auth=(self._user, self._password))

        if r.status_code < 200 or r.status_code >= 300:
            logger.error('error fetching url=%s status=%s content=%s' % (url, r.status_code, r.content or ''))
            raise ProviderError.externalProviderError("Scanpix request can't be performed")
        return r

    def _parse_doc(self, doc):
        new_doc = {}
        new_doc['_id'] = doc['refPtr']
        new_doc['guid'] = doc['refPtr']
        try:
            new_doc['description_text'] = doc['caption']
        except KeyError:
            pass
        try:
            new_doc['headline'] = doc['headline']
        except KeyError:
            pass
        try:
            new_doc['original_source'] = new_doc['source'] = doc['credit']
        except KeyError:
            pass
        new_doc['versioncreated'] = new_doc['firstcreated'] = self._datetime(local_to_utc(SCANPIX_TZ, get_date(doc['archivedTime'])))
        new_doc['pubstatus'] = 'usable'
        # This must match the action
        new_doc['_type'] = 'externalsource'
        # entry that the client can use to identify the fetch endpoint
        new_doc['fetch_endpoint'] = 'scanpix'

        # mimetype is not directly found in Scanpix API
        # so we use original filename to guess it
        mimetype = mimetypes.guess_type("_{}".format(splitext(doc.get('originalFileName', ''))[1]))[0]
        if mimetype is None:
            # nothing found with filename, we try out luck with fileFormat
            try:
                format_ = doc['fileFormat'].split()[0]
            except (KeyError, IndexError):
                mimetype = None
            else:
                mimetype = mimetypes.guess_type('_.{}'.format(format_))[0]
        if mimetype is not None:
            new_doc['mimetype'] = mimetype

        main_group = doc['mainGroup']
        if main_group == 'video':
            new_doc[ITEM_TYPE] = CONTENT_TYPE.VIDEO
        else:
            new_doc[ITEM_TYPE] = CONTENT_TYPE.PICTURE

        try:
            doc_previews = doc['previews']
        except KeyError:
            logger.warning('no preview found for item {}'.format(new_doc['_id']))
        else:
            # we look for best available scanpix preview
            available_previews = [p['type'] for p in doc_previews]
            renditions = new_doc['renditions'] = {}
            for rend, previews in REND2PREV.items():
                for prev in previews:
                    if prev in available_previews:
                        idx = available_previews.index(prev)
                        renditions[rend] = {"href": doc_previews[idx]['url']}
                        break

        new_doc['byline'] = doc['byline']
        doc.clear()
        doc.update(new_doc)

    def _parse_hits(self, hits):
        hits['docs'] = hits.pop('data')
        hits['total'] = hits.pop('numResults')
        for doc in hits['docs']:
            self._parse_doc(doc)
        return hits

    def _datetime(self, string):
        try:
            return arrow.get(string).datetime
        except Exception:
            return utcnow()

    def find_all(self, resource, max_results=1000):
        raise NotImplementedError

    def find_one(self, resource, req, **lookup):
        raise NotImplementedError

    def find_one_raw(self, resource, _id):
        # XXX: preview is used here instead of paid download
        #      see SDNTB-15
        data = {}
        url = self._app.config['SCANPIX_SEARCH_URL'] + '/search'
        data['refPtrs'] = [_id]
        r = self._request(url, data)
        doc = r.json()['data'][0]
        self._parse_doc(doc)

        url = doc['renditions']['baseImage']['href']
        # if MIME type can't be guessed, we default to jpeg
        mime_type = mimetypes.guess_type(url)[0] or 'image/jpeg'

        r = self._request(url, data)
        out = BytesIO(r.content)
        file_name, content_type, metadata = process_file_from_stream(out, mime_type)

        logger.debug('Going to save media file with %s ' % file_name)
        out.seek(0)
        try:
            file_id = self._app.media.put(out, filename=file_name, content_type=content_type, metadata=None)
        except Exception as e:
            logger.exception(e)
            raise SuperdeskApiError.internalError('Media saving failed')
        else:
            try:
                inserted = [file_id]
                doc['mimetype'] = content_type
                doc['filemeta'] = decode_metadata(metadata)
                # set the version created to now to bring it to the top of the desk, images can be quite old
                doc['versioncreated'] = utcnow()
                file_type = content_type.split('/')[0]
                rendition_spec = get_renditions_spec()
                renditions = generate_renditions(out, file_id, inserted, file_type,
                                                 content_type, rendition_spec,
                                                 url_for_media, insert_metadata=False)
                doc['renditions'] = renditions
            except (IndexError, KeyError, json.JSONDecodeError) as e:
                logger.exception("Internal error: {}".format(e))
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
