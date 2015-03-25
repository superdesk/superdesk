
import superdesk
from bs4 import BeautifulSoup


def join_html(pieces):
    """Join given list with line breaks.

    :param pieces: list of str
    """
    return '\n'.join(pieces)


def item_to_str(item):
    """Get text representation of a given item.

    :param item: news item
    """

    pieces = []
    pieces.append('<h2>%s</h2>' % item.get('headline', ''))
    html = item.get('body_html')
    if html:
        soup = BeautifulSoup(html)
        pieces.append(str(soup.p))
    return join_html(pieces)


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

            doc.clear()
            doc['type'] = 'text'
            doc['headline'] = package.get('headline')
            doc['slugline'] = package.get('slugline')
            doc['byline'] = package.get('byline')
            doc['task'] = package.get('task')
            doc['family_id'] = package.get('guid')

            body = []
            for group in package.get('groups', []):
                for ref in group.get('refs', []):
                    if 'residRef' in ref:
                        item = service.find_one(req=None, _id=ref.get('residRef'))
                        body.append(item_to_str(item))
                        body.append('<p></p>')
            doc['body_html'] = join_html(body)

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
