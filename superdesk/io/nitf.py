"""Simple NITF parser"""

from datetime import datetime
import xml.etree.ElementTree as etree
from superdesk.io import Parser

ITEM_CLASS_TEXT = 'text'
ITEM_CLASS_PRE_FORMATTED = 'preformatted'

subject_fields = ('tobject.subject.type', 'tobject.subject.matter', 'tobject.subject.detail')


class NITFParser(Parser):
    """
    NITF Parser
    """

    def parse_message(self, tree):
        item = {}
        docdata = tree.find('head/docdata')
        # set the default type.
        item['type'] = ITEM_CLASS_TEXT
        item['guid'] = item['uri'] = docdata.find('doc-id').get('id-string')
        item['urgency'] = docdata.find('urgency').get('ed-urg', '5')
        item['firstcreated'] = self.get_norm_datetime(docdata.find('date.issue'))
        item['versioncreated'] = self.get_norm_datetime(docdata.find('date.issue'))
        item['subject'] = self.get_subjects(tree)
        item['body_html'] = self.get_content(tree)
        item['pubstatus'] = docdata.attrib.get('management-status', 'usable')

        item['headline'] = tree.find('body/body.head/hedline/hl1').text

        elem = tree.find('body/body.head/abstract')
        item['abstract'] = elem.text if elem is not None else ''

        elem = tree.find('body/body.head/dateline/location/city')
        item['dateline'] = elem.text if elem is not None else ''
        item['byline'] = self.get_byline(tree)

        # try:
        #     item['copyrightholder'] = docdata.find('doc.copyright').get('holder')
        # except AttributeError:
        #     pass

        self.parse_meta(tree, item)

        return item

    def get_byline(self, tree):
        elem = tree.find('body/body.head/byline')
        byline = ''
        if elem is not None:
            byline = elem.text
            person = elem.find('person')
            if person is not None:
                byline = "{} {}".format(byline, person.text)

        return byline

    def get_norm_datetime(self, tree):
        return datetime.strptime(tree.attrib['norm'], '%Y%m%dT%H%M%S')

    def get_content(self, tree):
        elements = []
        for elem in tree.find('body/body.content'):
            elements.append(etree.tostring(elem, encoding='UTF-8').decode('utf-8'))
        return ''.join(elements)

    def parse_meta(self, tree, item):
        for elem in tree.findall('head/meta'):
            attribute_name = elem.get('name')

            if attribute_name == 'anpa-keyword':
                item['slugline'] = elem.get('content')
            if attribute_name == 'anpa-sequence':
                item['ingest_provider_sequence'] = elem.get('content')
            if attribute_name == 'anpa-wordcount':
                item['word_count'] = elem.get('content')
            if attribute_name == 'anpa-takekey':
                item['anpa_take_key'] = elem.get('content')
            if attribute_name == 'anpa-format':
                anpa_format = elem.get('content').lower() if elem.get('content') is not None else 'x'
                item['type'] = ITEM_CLASS_TEXT if anpa_format == 'x' else ITEM_CLASS_PRE_FORMATTED

    def get_subjects(self, tree):
        subjects = []
        for elem in tree.findall('head/tobject/tobject.subject'):
            qcode = elem.get('tobject.subject.refnum')
            for field in subject_fields:
                if elem.get(field):
                    subjects.append({
                        'name': elem.get(field)
                    })

            if len(subjects):
                subjects[-1]['code'] = qcode

        return subjects
