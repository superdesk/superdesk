import os

import flask
import eve

from superdesk import utils
from decorators import crossdomain

def items_get(resource, documents):
    """Prefix local storage contents with MEDIA_URL."""
    for doc in documents:
        if 'contents' in doc:
            for content in doc['contents']:
                try:
                    content['url'] = app.config.get('MEDIA_URL') + content['storage']
                except KeyError:
                    pass

class Auth(eve.auth.TokenAuth):
    def check_auth(self, token, allowed_roles, resource):
        auth_token = app.data.driver.db.auth_tokens.find_one({'token': token})
        return auth_token

class AuthException(Exception):
    pass

app = eve.Eve(auth=Auth, settings=os.path.join(os.path.dirname(__file__), 'settings.py'))
app.on_getting += items_get

@app.route('/auth/', methods=['POST', 'OPTIONS'])
@crossdomain('*', headers=['X-Requested-With', 'Content-Type'])
def auth():
    try:
        data = flask.request.get_json()
        if not data:
            raise AuthException(400, "invalid credentials")

        user = app.data.driver.db.users.find_one({'username': data.get('username')})
        if not user:
            raise AuthException(400, "username not found")

        if user.get('password') != data.get('password'):
            raise AuthException(400, "invalid credentials")

        user.pop('_id', None)
        user.pop('password', None)

        auth_token = {
            'user': user,
            'token': utils.get_random_string(40)
        }
        app.data.driver.db.auth_tokens.insert(auth_token)

        auth_token.pop('_id', None)
        return (flask.jsonify(auth_token), 201)
    except AuthException as err:
        return (flask.jsonify({'message': '%d: %s' % (err.args[0], err.args[1])}), err.args[0])

if __name__ == '__main__':
    app.run(debug=True)
