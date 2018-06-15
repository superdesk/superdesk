
from bs4 import BeautifulSoup
from superdesk import get_resource_service


def text(val):
    if not val:
        return ''
    soup = BeautifulSoup(val, 'html.parser')
    return soup.text


def populate(item, **kwargs):
    analysis = get_resource_service('analysis')
    data = {
        'lang': 'ENG' if item.get('language', '') == 'en' else 'ITA',
        'text': '\n'.join([
            text(item.get('abstract', '')),
            text(item.get('body_html', '')),
            text(item.get('description_text', '')),
        ]),
        'title': text(item.get('headline', '')),
    }
    analysed = analysis.do_analyse(data)
    for key, val in analysed.items():
        if not item.get(key):
            item[key] = val
    if analysed.get('semantics'):
        item['semantics'] = analysed['semantics']
    if analysed.get('subject'):
        item['subject'] = [s for s in item['subject'] if s.get('scheme')]  # filter out iptc subjectcodes
        item['subject'].extend(analysed['subject'])
    if analysed.get('abstract') and not item.get('abstract'):
        item.setdefault('abstract', analysed['abstract'])
    return item


name = 'populate_semantics'
label = 'Populate Semantics'
callback = populate
access_type = 'backend'
action_type = 'direct'
