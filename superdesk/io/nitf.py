"""Simple NITF parser"""

import datetime
import xml.etree.ElementTree as etree

from .iptc import subject_codes

ITEM_CLASS = 'icls:text'

def get_norm_datetime(tree):
    return datetime.datetime.strptime(tree.attrib['norm'], '%Y%m%dT%H%M%S')

def get_contents(tree):
    content = {}
    content['contenttype'] = 'application/xhtml+html'

    elements = []
    for elem in tree.find('body/body.content'):
        elements.append(etree.tostring(elem, encoding='UTF-8').decode('utf-8'))
    content['content'] = ''.join(elements)
    return [content]

def get_keywords(tree):
    keywords = []
    for elem in tree.findall('head/meta'):
        if elem.get('name') == 'anpa-keyword':
            keywords.append(elem.get('content'))
    return keywords

def is_matching_qcode(x, y):
    """Test if x matches y qcode.

    x: 02000000 matches y: 02003000 but x: 02001000 doesn't match 02003000
    """
    for i, xi in enumerate(x):
        if xi != '0' and xi != y[i]:
            return False
    return True

def expand_qcode(qcode):
    for key, val in subject_codes.items():
        if is_matching_qcode(key, qcode):
            yield {'qcode': key, 'name': val}
    return []

def get_subjects(tree):
    subjects = []
    for elem in tree.findall('head/tobject/tobject.subject'):
        qcode = elem.get('tobject.subject.refnum')
        for subject in expand_qcode(qcode):
            subjects.append(subject)
    return subjects

def parse(text):
    item = {}
    tree = etree.fromstring(text.encode('utf-8'))
    docdata = tree.find('head/docdata')

    item['itemClass'] = ITEM_CLASS
    item['headline'] = tree.find('head/title').text
    item['guid'] = docdata.find('doc-id').get('id-string')
    item['urgency'] = int(docdata.find('urgency').get('ed-urg', 5))
    item['firstCreated'] = get_norm_datetime(docdata.find('date.issue'))
    item['versionCreated'] = get_norm_datetime(docdata.find('date.issue'))
    item['contents'] = get_contents(tree)
    item['keywords'] = get_keywords(tree)
    item['subjects'] = get_subjects(tree)

    try:
        item['copyrightHolder'] = docdata.find('doc.copyright').get('holder')
    except AttributeError:
        pass

    try:
        item['rightsInfo'] = docdata.find('doc.rights').attrib
    except AttributeError:
        pass

    return item
