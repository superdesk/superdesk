
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
        'lang': 'ITA' if item.get('language', '') == 'it' else 'ENG',
        'text': '\n'.join([
            text(item.get('abstract', '')),
            text(item.get('body_html', '')),
            text(item.get('description_text', '')),
        ]),
        'title': text(item.get('headline', '')),
    }
    item['semantics'] = analysis.do_analyse(data)
    return item


name = 'populate_semantics'
label = 'Populate Semantics'
callback = populate
access_type = 'backend'
action_type = 'direct'
