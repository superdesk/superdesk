
import os
import eve
import superdesk
from flask import request

class SuperdeskTokenAuth(eve.auth.TokenAuth):
    """Superdesk Token Auth"""

    def check_auth(self, token, allowed_roles, resource, method):
        """Check if given token is valid"""
        return app.data.find_one('auth', token=token)

class SuperdeskEve(eve.Eve):
    """Superdesk API"""

    def load_config(self):
        """Let us override settings withing plugins"""

        super(SuperdeskEve, self).load_config()
        self.config.from_object(superdesk)

abspath = os.path.abspath(os.path.dirname(__file__))
app = SuperdeskEve(data=superdesk.SuperdeskDataLayer, auth=SuperdeskTokenAuth, settings=os.path.join(abspath, 'settings.py'))
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
