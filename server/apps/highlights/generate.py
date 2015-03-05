
import superdesk
from bs4 import BeautifulSoup


class GenerateHighlightsService(superdesk.Service):
    def create(self, docs, **kwargs):
        """Generate highlights text item for given package.

        If doc.preview is True it won't save the item, only return.
        """
        service = superdesk.get_resource_service('archive')

        ids = []
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

            body = []
            for group in package.get('groups', []):
                for ref in group.get('refs', []):
                    item = service.find_one(req=None, _id=ref['residRef'])
                    body.append('<h2>%s</h2>' % item.get('headline', ''))
                    soup = BeautifulSoup(item.get('body_html', ''))
                    body.append(str(soup.p))
            doc['body_html'] = '\n'.join(body)

            if preview:
                ids.append('')
            else:
                ids.append(service.create([doc], **kwargs))

        return ids


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
