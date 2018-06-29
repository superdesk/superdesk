
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
    analysis.apply(analysed, item)
    return item


name = 'populate_semantics'
label = 'Populate Semantics'
callback = populate
access_type = 'backend'
action_type = 'direct'
