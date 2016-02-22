
# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
from bson import ObjectId

import superdesk
import urllib3
import urllib
import xml.etree.ElementTree as etree
import pytz
from pytz import NonExistentTimeError, AmbiguousTimeError
from superdesk import config
from superdesk.io.iptc import subject_codes
from datetime import datetime
import time
from superdesk.metadata.item import ITEM_TYPE, CONTENT_TYPE, ITEM_STATE, CONTENT_STATE
from superdesk.io.commands.update_ingest import process_iptc_codes
from superdesk.etree import get_text_word_count
from apps.archive.common import generate_unique_id_and_name
import json
from eve.utils import ParsedRequest


# The older content does not contain an anpa category, so we derive it from the
# publication name
pubnames = {
    'International Sport': 's',
    'Racing': 'r',
    'Parliamentary Press Releases': 'p',
    'Features': 'c',
    'Financial News': 'f',
    'General': 'a',
    'aap Features': 'c',
    'aap International News': 'i',
    'aap Australian Sport': 't',
    'Australian General News': 'a',
    'Asia Pulse Full': 'i',
    'AFR Summary': 'a',
    'Australian Sport': 't',
    'PR Releases': 'j',
    'Entertainment News': 'e',
    'Special Events': 'y',
    'Asia Pulse': 'i',
    'aap International Sport': 's',
    'Emergency Services': 'a',
    'BRW Summary': 'a',
    'FBM Summary': 'a',
    'aap Australian General News': 'a',
    'International News': 'i',
    'aap Financial News': 'f',
    'Asia Pulse Basic': 'i',
    'Political News': 'p',
    'Advisories': 'v'
}


class AppImportTextArchiveCommand(superdesk.Command):

    option_list = (
        superdesk.Option('--start', '-strt', dest='start_id', required=True),
        superdesk.Option('--user', '-usr', dest='user', required=True),
        superdesk.Option('--password', '-pwd', dest='password', required=True),
        superdesk.Option('--url_root', '-url', dest='url', required=True),
        superdesk.Option('--query', '-qry', dest='query', required=True),
        superdesk.Option('--count', '-c', dest='limit', required=False),
        superdesk.Option('--direction', '-d', dest='direction', required=False)
    )

    BATCH_SIZE = 500

    def run(self, start_id, user, password, url, query, limit, direction):
        print('Starting text archive import at {}'.format(start_id))
        self._user = user
        self._password = password
        self._id = int(start_id)
        self._url_root = url
        self._query = urllib.parse.quote(query)
        # direction True is forwards
        self._direction = True
        if direction is not None:
            if direction.lower()[0] == 'r':
                self._direction = False
        if limit is not None:
            self._limit = int(limit)
        else:
            self._limit = None

        self._api_login()

        x = self._get_bunch(self._id)
        while x:
            self._process_bunch(x)
            x = self._get_bunch(self._id)
            if self._limit is not None and self._limit <= 0:
                break
            if limit is None and int(x.find('doc_count').text) == 0:
                print('Complete')
                break

        print('finished text archive import')

    def _api_login(self):
        self._http = urllib3.PoolManager()
        credentials = '?login[username]={}&login[password]={}'.format(self._user, self._password)
        url = self._url_root + credentials
        r = self._http.urlopen('GET', url, headers={'Content-Type': 'application/xml'})
        self._headers = {'cookie': r.getheader('set-cookie')}

        self._anpa_categories = superdesk.get_resource_service('vocabularies').find_one(req=None, _id='categories')

    def _get_bunch(self, id):
        url = self._url_root
        if self._direction:
            d = '>'
        else:
            d = '<'
        url += 'archives/txtarch?search_docs[struct_query]=(DCDATA_ID{0}{1})&search_docs[query]='.format(d, id)
        url += self._query
        url += '&search_docs[format]=full&search_docs[pagesize]={0}&search_docs[page]=1'.format(self.BATCH_SIZE)
        if self._direction:
            url += '&search_docs[sortorder]=DCDATA_ID%20ASC'
        else:
            url += '&search_docs[sortorder]=DCDATA_ID%20DESC'
        print('Getting batch from DC url [{0}]'.format(url))
        retries = 3
        while retries > 0:
            s = time.time()
            r = self._http.request('GET', url, headers=self._headers)
            print('DC returned in {:.2f} seconds'.format(time.time() - s))
            if r.status == 200:
                e = etree.fromstring(r.data)
                # print(str(r.data))
                count = int(e.find('doc_count').text)
                if count > 0:
                    print('count : {}'.format(count))
                return e
            else:
                self._api_login()
                retries -= 1
        return None

    def _get_head_value(self, doc, field):
        el = doc.find('dcdossier/document/head/' + field)
        if el is not None:
            return el.text
        return None

    def _addkeywords(self, key, doc, item):
            code = self._get_head_value(doc, key)
            if code:
                if 'keywords' not in item:
                    item['keywords'] = []
                item['keywords'].append(code)

    def _process_bunch(self, x):
        # x.findall('dc_rest_docs/dc_rest_doc')[0].get('href')
        items = []
        for doc in x.findall('dc_rest_docs/dc_rest_doc'):
            try:
                # print(doc.get('href'))
                id = doc.find('dcdossier').get('id')
                if self._direction:
                    if int(id) > self._id:
                        self._id = int(id)
                else:
                    if int(id) < self._id:
                        self._id = int(id)
                item = {}
                item['guid'] = doc.find('dcdossier').get('guid')

                # if the item has been modified in the archive then it is due to a kill
                # there is an argument that this item should not be imported at all
                if doc.find('dcdossier').get('created') != doc.find('dcdossier').get('modified'):
                    # item[ITEM_STATE] = CONTENT_STATE.KILLED
                    continue
                else:
                    item[ITEM_STATE] = CONTENT_STATE.PUBLISHED

                value = datetime.strptime(self._get_head_value(doc, 'PublicationDate'), '%Y%m%d%H%M%S')
                local_tz = pytz.timezone('Australia/Sydney')
                try:
                    aus_dt = local_tz.localize(value, is_dst=None)
                except NonExistentTimeError as ex:
                    aus_dt = local_tz.localize(value, is_dst=True)
                except AmbiguousTimeError:
                    aus_dt = local_tz.localize(value, is_dst=False)

                item['firstcreated'] = aus_dt.astimezone(pytz.utc)
                item['versioncreated'] = item['firstcreated']

                generate_unique_id_and_name(item)
                item['ingest_id'] = id

                item['source'] = self._get_head_value(doc, 'Agency')

    #            self._addkeywords('AsiaPulseCodes', doc, item)

                byline = self._get_head_value(doc, 'Byline')
                if byline:
                    item['byline'] = byline

                # item['service'] = self._get_head_value(doc,'Service')

                category = self._get_head_value(doc, 'Category')
                if not category:
                    publication_name = self._get_head_value(doc, 'PublicationName')
                    if publication_name in pubnames:
                        category = pubnames[publication_name]
                if category:
                    anpacategory = {}
                    anpacategory['qcode'] = category
                    for anpa_category in self._anpa_categories['items']:
                        if anpacategory['qcode'].lower() == anpa_category['qcode'].lower():
                            anpacategory = {'qcode': anpacategory['qcode'], 'name': anpa_category['name']}
                            break
                    item['anpa_category'] = [anpacategory]

    #           self._addkeywords('CompanyCodes', doc, item)

                type = self._get_head_value(doc, 'Format')
                if type == 'x':
                    item[ITEM_TYPE] = CONTENT_TYPE.TEXT
                elif type == 't':
                    item[ITEM_TYPE] = CONTENT_TYPE.PREFORMATTED
                else:
                    item[ITEM_TYPE] = CONTENT_TYPE.TEXT

                item['keyword'] = self._get_head_value(doc, 'Keyword')
                item['ingest_provider_sequence'] = self._get_head_value(doc, 'Sequence')

                orginal_source = self._get_head_value(doc, 'Author')
                if orginal_source:
                    item['original_source'] = orginal_source

                item['headline'] = self._get_head_value(doc, 'Headline')

                code = self._get_head_value(doc, 'SubjectRefNum')
                if code and len(code) == 7:
                    code = '0' + code
                if code and code in subject_codes:
                    item['subject'] = []
                    item['subject'].append({'qcode': code, 'name': subject_codes[code]})
                    try:
                        process_iptc_codes(item, None)
                    except:
                        pass

                slug = self._get_head_value(doc, 'SLUG')
                if slug:
                    item['slugline'] = slug
                else:
                    item['slugline'] = self._get_head_value(doc, 'Keyword')

                take_key = self._get_head_value(doc, 'Takekey')
                if take_key:
                    item['anpa_take_key'] = take_key

    #            self._addkeywords('Topic', doc, item)

    #            self._addkeywords('Selectors', doc, item)

                el = doc.find('dcdossier/document/body/BodyText')
                if el is not None:
                    story = el.text
                    if item[ITEM_TYPE] == CONTENT_TYPE.TEXT:
                        story = story.replace('\n   ', '<br><br>')
                        story = story.replace('\n', '<br>')
                        item['body_html'] = story
                    else:
                        item['body_html'] = story
                    try:
                        item['word_count'] = get_text_word_count(item['body_html'])
                    except:
                        pass

                item['pubstatus'] = 'usable'
                # this is required for the archived service additional lookup
                item['item_id'] = item['guid']
                item[config.VERSION] = 1
                item['flags'] = {'marked_archived_only': True}

                # item['_id'] = ObjectId(id.rjust(24,'0'))
                item['_id'] = ObjectId()
                items.append(item)

                if self._limit:
                    self._limit -= 1
                # print(item)
            except Exception as ex:
                print('Exception parsing DC documnent {}'.format(id))
                pass

        try:
            res = superdesk.get_resource_service('archived')
            s = time.time()
            res.post(items)
            print('Post to Batch to Superdesk took {:.2f}'.format(time.time() - s))
        except Exception as ex:
            if ex.code == 409:
                print('Key clash exceptionn detected')
                # create a list of the guids we tried to post
                guids = [g['guid'] for g in items]
                # create a query for all those id's
                query = {
                    'size': self.BATCH_SIZE,
                    'query': {
                        'filtered': {
                            'filter': {
                                "terms": {
                                    "guid": [guids]
                                }
                            }
                        }
                    }
                }

                req = ParsedRequest()
                repos = 'archived'
                req.args = {'source': json.dumps(query), 'repo': repos}

                search_res = superdesk.get_resource_service('search')
                existing = search_res.get(req=req, lookup=None)
                existing_guids = [e['guid'] for e in existing]
                not_existing = [g for g in guids if g not in existing_guids]
                for missing_guid in not_existing:
                    i = [m for m in items if m['guid'] == missing_guid]
                    original = res.find_one(req=None, guid=i[0]['guid'])
                    if not original:
                        try:
                            s = time.time()
                            res.post(i)
                            print('Post single item to Superdesk in {:.2f} seconds'.format(time.time() - s))
                        except Exception as ex:
                            print('Exception posting single item')
            else:
                print('Exception posting batch')


superdesk.command('app:import_text_archive', AppImportTextArchiveCommand())
