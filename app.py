import os

from eve import Eve
from eve.utils import config
from eve.auth import TokenAuth


def items_get(resource, documents):
    """Prefix local storage contents with MEDIA_URL."""
    for doc in documents:
        if 'contents' in doc:
            for content in doc['contents']:
                try:
                    content['url'] = config.MEDIA_URL + content['storage']
                except KeyError:
                    pass

class Auth(TokenAuth):
    def check_auth(self, token, allowed_roles, resource):
        return token == 'secret'


app = Eve(auth=Auth)
app.on_getting += items_get

if __name__ == '__main__':
    app.run(debug=True)
