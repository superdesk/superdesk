
import os
import eve
import superdesk
from flask import request

class SuperdeskTokenAuth(eve.auth.TokenAuth):
    """Superdesk Token Auth"""

    def check_auth(self, token, allowed_roles, resource, method):
        """Check if given token is valid."""
        return application.data.find_one('auth', token=token)

class SuperdeskEve(eve.Eve):
    """Superdesk API"""

    def load_config(self):
        """Let us override settings withing plugins"""

        super(SuperdeskEve, self).load_config()
        self.config.from_object(superdesk)

abspath = os.path.abspath(os.path.dirname(__file__))
application = SuperdeskEve(data=superdesk.SuperdeskData, auth=SuperdeskTokenAuth, settings=os.path.join(abspath, 'settings.py'))

application.on_fetch_resource = superdesk.proxy_resource_signal('read', application)
application.on_fetch_item = superdesk.proxy_item_signal('read', application)

superdesk.app = application

if __name__ == '__main__':
    application.run(debug=True)
