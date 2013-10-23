"""Simple NITF parser"""

import datetime
import xml.etree.ElementTree as etree

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

def parse(text):
    item = {}
    tree = etree.fromstring(text.encode('utf-8'))
    docdata = tree.find('head/docdata')
    item['itemClass'] = ITEM_CLASS
    item['headline'] = tree.find('head/title').text
    item['guid'] = docdata.find('doc-id').attrib['id-string']
    item['urgency'] = int(docdata.find('urgency').attrib['ed-urg'])
    item['firstCreated'] = get_norm_datetime(docdata.find('date.issue'))
    item['versionCreated'] = get_norm_datetime(docdata.find('date.issue'))
    item['contents'] = get_contents(tree)

    try:
        item['copyrightHolder'] = docdata.find('doc.copyright').attrib['holder']
    except AttributeError:
        pass

    return item
