
import os
import eve
from flask import request
import superdesk

class SuperdeskTokenAuth(eve.auth.TokenAuth):
    """Superdesk Token Auth"""

    def check_auth(self, token, allowed_roles, resource, method):
        """Check if given token is valid."""
        return application.data.find_one('auth', token=token)

class SuperdeskEve(eve.Eve):
    """Eve Wrapper"""

    def load_config(self):
        """Let us override settings withing plugins"""

        super(SuperdeskEve, self).load_config()
        self.config.from_object(superdesk)

abspath = os.path.abspath(os.path.dirname(__file__))
application = SuperdeskEve(data=superdesk.SuperdeskData, auth=SuperdeskTokenAuth, settings=os.path.join(abspath, 'settings.py'))

if __name__ == '__main__':
    application.run(debug=application.config.get('DEBUG'))
