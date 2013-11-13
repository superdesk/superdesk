"""Simple NITF parser"""

from datetime import datetime
import xml.etree.ElementTree as etree

from .iptc import subject_codes

ITEM_CLASS = 'text'

subject_fields = ('tobject.subject.type', 'tobject.subject.matter', 'tobject.subject.detail')

def get_norm_datetime(tree):
    return datetime.strptime(tree.attrib['norm'], '%Y%m%dT%H%M%S')

def get_content(tree):
    elements = []
    for elem in tree.find('body/body.content'):
        elements.append(etree.tostring(elem, encoding='UTF-8').decode('utf-8'))
    return ''.join(elements)

def get_keywords(tree):
    keywords = []
    for elem in tree.findall('head/meta'):
        if elem.get('name') == 'anpa-keyword':
            keywords.append(elem.get('content'))
    return keywords

def get_subjects(tree):
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

def parse(text):
    item = {}
    tree = etree.fromstring(text.encode('utf-8'))
    docdata = tree.find('head/docdata')

    item['type'] = ITEM_CLASS
    item['headline'] = tree.find('head/title').text
    item['guid'] = item['uri'] = docdata.find('doc-id').get('id-string')
    item['urgency'] = docdata.find('urgency').get('ed-urg', '5')
    item['firstcreated'] = get_norm_datetime(docdata.find('date.issue'))
    item['versioncreated'] = get_norm_datetime(docdata.find('date.issue'))
    item['keywords'] = get_keywords(tree)
    item['subject'] = get_subjects(tree)
    item['body_html'] = get_content(tree)
    item['pubstatus'] = docdata.attrib.get('management-status', 'usable')

    try:
        item['copyrightHolder'] = docdata.find('doc.copyright').get('holder')
    except AttributeError:
        pass

    try:
        item['rightsInfo'] = docdata.find('doc.rights').attrib
    except AttributeError:
        pass

    return item
