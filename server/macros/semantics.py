
from bs4 import BeautifulSoup
from superdesk import get_resource_service, config


def text(val):
    if not val:
        return ''
    soup = BeautifulSoup(val, 'html.parser')
    return soup.text


def populate(item, **kwargs):
    analysis = get_resource_service('analysis')
    data = {
        'lang': 'ITA',
        'text': '\n'.join([text(item.get('abstract')), text(item.get('body_html', ''))]),
        'title': text(item.get('headline', '')),
    }
    item['semantics'] = analysis.do_analyse(data)
    return item
    #get_resource_service('archive').patch(id=item[config.ID_FIELD], updates=updates)


name = 'populate_semantics'
label = 'Populate Semantics'
callback = populate
access_type = 'backend'
action_type = 'direct'
