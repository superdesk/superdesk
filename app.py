
import os
import eve
import superdesk
import flask
from eve.io.mongo import MongoJSONEncoder


class SuperdeskTokenAuth(eve.auth.TokenAuth):
    """Superdesk Token Auth"""

    def check_auth(self, token, allowed_roles, resource, method):
        """Check if given token is valid"""
        auth_token = app.data.find_one('auth', token=token)
        if auth_token:
            flask.g.user = app.data.find_one('users', _id=(str(auth_token['user']['_id'])))
        return auth_token


class SuperdeskEve(eve.Eve):
    """Superdesk API"""

    def load_config(self):
        """Let us override settings withing plugins"""

        super(SuperdeskEve, self).load_config()
        self.config.from_object(superdesk)

abspath = os.path.abspath(os.path.dirname(__file__))
app = SuperdeskEve(
    data=superdesk.SuperdeskDataLayer,
    auth=SuperdeskTokenAuth,
    settings=os.path.join(abspath, 'settings.py'),
    json_encoder=MongoJSONEncoder)
app.on_fetch_resource = superdesk.proxy_resource_signal('read', app)
app.on_fetch_item = superdesk.proxy_item_signal('read', app)
superdesk.app = app

for blueprint in superdesk.BLUEPRINTS:
    app.register_blueprint(blueprint, **blueprint.kwargs)

if __name__ == '__main__':

    if 'PORT' in os.environ:
        port = int(os.environ.get('PORT'))
        host = '0.0.0.0'
        app.debug = 'SUPERDESK_DEBUG' in os.environ
    else:
        port = 5000
        host = '127.0.0.1'
        app.debug = True

    app.run(host=host, port=port)
