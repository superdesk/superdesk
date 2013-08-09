import os

from flask import request, jsonify
from eve import Eve
from eve.utils import config
from eve.auth import TokenAuth

from superdesk import utils


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
        auth_token = app.data.driver.db.auth_tokens.find_one({'token': token})
        return auth_token


app = Eve(auth=Auth)
app.on_getting += items_get

@app.route('/auth', methods=['POST'])
def auth():
    user = app.data.driver.db.users.find_one({'username': request.form.get('username')})
    if not user:
        return ('username not found', 400)

    if user.get('password') == request.form.get('password'):
        auth_token = {
            'user': user,
            'token': utils.get_random_string(40)
        }
        app.data.driver.db.auth_tokens.insert(auth_token)
        return jsonify({'token': auth_token.get('token')})
    else:
        return ('password is not valid', 400)

if __name__ == '__main__':
    app.run(debug=True)
