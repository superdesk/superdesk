
# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import superdesk
import urllib3
import urllib
import xml.etree.ElementTree as etree
from superdesk.io.iptc import subject_codes
from datetime import datetime
from superdesk.utc import utc

# The older content does not contain an anpa category, so we derive it from the
# publication name
pubnames = {
    'International Sport': 'S',
    'Racing': 'H',  # WRONG
    'Parliamentary Press Releases': 'P',
    'Features': 'C',
    'Financial News': 'F',
    'General': 'A',
    'aap Features': 'C',
    'aap International News': 'I',
    'aap Australian Sport': 'S',
    'Australian General News': 'A',
    'Asia Pulse Full': 'I',
    'AFR Summary': 'A',
    'Australian Sport': 'T',
    'PR Releases': 'J',
    'Entertainment News': 'E',
    'Special Events': 'Y',
    'Asia Pulse': 'I',
    'aap International Sport': 'S',
    'Emergency Services': 'A',
    'BRW Summary': 'A',
    'FBM Summary': 'A',
    'aap Australian General News': 'A',
    'International News': 'I',
    'aap Financial News': 'F',
    'Asia Pulse Basic': 'I',
    'Political News': 'P',
    'Advisories': 'V'
}


class AppImportTextArchiveCommand(superdesk.Command):

    option_list = (
        superdesk.Option('--start', '-strt', dest='start_id', required=False),
        superdesk.Option('--user', '-usr', dest='user', required=True),
        superdesk.Option('--password', '-pwd', dest='password', required=True),
        superdesk.Option('--url_root', '-url', dest='url', required=True),
        superdesk.Option('--query', '-qry', dest='query', required=True)
    )

    def _api_login(self):
        self._http = urllib3.PoolManager()
        credentials = '?login[username]={}&login[password]={}'.format(self._user, self._password)
        url = self._url_root + credentials
        r = self._http.urlopen('GET', url, headers={'Content-Type': 'application/xml'})
        self._headers = {'cookie': r.getheader('set-cookie')}

        self._anpa_categories = superdesk.get_resource_service('vocabularies').find_one(req=None, _id='categories')

    def _get_bunch(self, id):
        url = self._url_root + 'archives/txtarch?search_docs[query]=(ID<{0})'.format(id)
        url += self._query
        url += '&search_docs[format]=full&search_docs[pagesize]=100&search_docs[page]=1'
        url += '&search_docs[sortorder]=DCDATA_ID%20DESC'
        print(url)
        r = self._http.request('GET', url, headers=self._headers)
        e = etree.fromstring(r.data)
        print(str(r.data))
        count = int(e.find('doc_count').text)
        if count > 0:
            print('count : {}'.format(count))
            return e
        return None

    def _get_head_value(self, doc, field):
        el = doc.find('dcdossier/document/head/' + field)
        if el is not None:
            return el.text
        return None

    def _process_iptc_codes(self, item):
        """
        Ensures that the higher level IPTC codes are present by inserting them if missing, for example
        if given 15039001 (Formula One) make sure that 15039000 (motor racing) and 15000000 (sport) are there as well

        :param item: A story item
        :return: A story item with possible expanded subjects
        """
        try:
            def iptc_already_exists(code):
                for entry in item['subject']:
                    if 'qcode' in entry and code == entry['qcode']:
                        return True
                return False

            for subject in item['subject']:
                if 'qcode' in subject and len(subject['qcode']) == 8:
                    top_qcode = subject['qcode'][:2] + '000000'
                    if not iptc_already_exists(top_qcode):
                        item['subject'].append({'qcode': top_qcode, 'name': subject_codes[top_qcode]})

                    mid_qcode = subject['qcode'][:5] + '000'
                    if not iptc_already_exists(mid_qcode):
                        item['subject'].append({'qcode': mid_qcode, 'name': subject_codes[mid_qcode]})
        except Exception:
            pass

    def _addkeywords(self, key, doc, item):
            code = self._get_head_value(doc, key)
            if code:
                if 'keywords' not in item:
                    item['keywords'] = []
                item['keywords'].append(code)

    def _process_bunch(self, x):
        # x.findall('dc_rest_docs/dc_rest_doc')[0].get('href')
        for doc in x.findall('dc_rest_docs/dc_rest_doc'):
            print(doc.get('href'))
            id = doc.find('dcdossier').get('id')
            if int(id) < self._id:
                self._id = int(id)
            item = {}
            item['guid'] = doc.find('dcdossier').get('guid')

            # if the item has been modified in the archive then it is due to a kill
            # there is an argument that this item should not be imported at all
            if doc.find('dcdossier').get('created') != doc.find('dcdossier').get('modified'):
                item['state'] = 'killed'
            else:
                item['state'] = 'published'

            value = datetime.strptime(self._get_head_value(doc, 'PublicationDate'), '%Y%m%d%H%M%S')
            item['firstcreated'] = utc.normalize(value) if value.tzinfo else value
            item['versioncreated'] = item['firstcreated']

            item['unique_id'] = doc.find('dcdossier').get('unique')
            item['ingest_id'] = id

            item['source'] = self._get_head_value(doc, 'Agency')

            self._addkeywords('AsiaPulseCodes', doc, item)

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
                item['anpa-category'] = {}
                item['anpa-category']['qcode'] = category
                for anpa_category in self._anpa_categories['items']:
                    if anpa_category['is_active'] is True \
                            and item['anpa-category']['qcode'].lower() == anpa_category['value'].lower():
                        item['anpa-category'] = {'qcode': item['anpa-category']['qcode'], 'name': anpa_category['name']}
                        break

            self._addkeywords('CompanyCodes', doc, item)

            type = self._get_head_value(doc, 'Format')
            if type == 'x':
                item['type'] = 'text'
            elif type == 't':
                item['type'] = 'preformated'
            else:
                item['type'] = 'text'

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
                self._process_iptc_codes(item)

            slug = self._get_head_value(doc, 'SLUG')
            if slug:
                item['slugline'] = slug
            else:
                item['slugline'] = self._get_head_value(doc, 'Keyword')

            # self._addkeywords('Takekey', doc, item)
            take_key = self._get_head_value(doc, 'Takekey')
            if take_key:
                item['anpa_take_key'] = take_key

            self._addkeywords('Topic', doc, item)

            self._addkeywords('Selectors', doc, item)

            if item['type'] == 'text':
                story = doc.find('dcdossier/document/body/BodyText').text
                story = story.replace('\n   ', '<br><br>')
                story = story.replace('\n', '<br>')
                item['body_html'] = story
            else:
                item['body_html'] = doc.find('dcdossier/document/body/BodyText').text

            item['pubstatus'] = 'usable'

            res = superdesk.get_resource_service('text_archive')
            original = res.find_one(req=None, guid=item['guid'])
            if not original:
                res.post([item])
            else:
                res.patch(original['_id'], item)

            print(item)

    def run(self, start_id, user, password, url, query):
        print('Starting text archive import at {}'.format(start_id))
        self._user = user
        self._password = password
        self._id = int(start_id)
        self._url_root = url
        self._query = urllib.parse.quote('&' + query)

        self._api_login()

        x = self._get_bunch(self._id)
        while x:
            self._process_bunch(x)
            x = self._get_bunch(self._id)

        print('finished text archive import')

superdesk.command('app:import_text_archive', AppImportTextArchiveCommand())
