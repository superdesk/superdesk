
import superdesk
from bs4 import BeautifulSoup
from superdesk.metadata.item import ITEM_TYPE, CONTENT_TYPE
from flask import render_template
from jinja2 import Template


def getTemplate(highlightId):
    """Return the string template associated with highlightId or none """
    if not highlightId:
        return None
    highlightService = superdesk.get_resource_service('highlights')
    highlight = highlightService.find_one(req=None, _id=highlightId)
    if not highlight or not highlight.get('template'):
        return None

    templateService = superdesk.get_resource_service('content_templates')
    template = templateService.find_one(req=None, _id=highlight.get('template'))
    if not template or 'body_html' not in template:
        return None
    return template.get('body_html')


class GenerateHighlightsService(superdesk.Service):
    def create(self, docs, **kwargs):
        """Generate highlights text item for given package.

        If doc.preview is True it won't save the item, only return.
        """
        service = superdesk.get_resource_service('archive')
        for doc in docs:
            preview = doc.get('preview', False)
            package = service.find_one(req=None, _id=doc['package'])
            if not package:
                superdesk.abort(404)
            stringTemplate = getTemplate(package.get('highlight'))

            doc.clear()
            doc[ITEM_TYPE] = CONTENT_TYPE.TEXT
            doc['headline'] = package.get('headline')
            doc['slugline'] = package.get('slugline')
            doc['byline'] = package.get('byline')
            doc['task'] = package.get('task')
            doc['family_id'] = package.get('guid')

            items = []
            for group in package.get('groups', []):
                for ref in group.get('refs', []):
                    if 'residRef' in ref:
                        item = service.find_one(req=None, _id=ref.get('residRef'))
                        if item:
                            html = item.get('body_html')
                            if html:
                                soup = BeautifulSoup(html)
                                item['first_paragraph_body_html'] = str(soup.p)
                            items.append(item)

            if stringTemplate:
                template = Template(stringTemplate)
                doc['body_html'] = template.render(package=package, items=items)
            else:
                doc['body_html'] = render_template('default_highlight_template.txt', package=package, items=items)
        if preview:
            return ['' for doc in docs]
        else:
            return service.post(docs, **kwargs)


class GenerateHighlightsResource(superdesk.Resource):
    """Generate highlights item for given package."""

    schema = {
        'package': {
            # not setting relation here, we will fetch it anyhow
            'type': 'string',
            'required': True,
        },
        'preview': {
            'type': 'boolean',
            'default': False,
        }
    }

    resource_methods = ['POST']
    item_methods = []
    privileges = {'POST': 'highlights'}
