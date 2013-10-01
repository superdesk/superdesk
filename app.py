
import os
import eve
import superdesk

class SuperdeskEve(eve.Eve):
    """Eve Wrapper"""

    def load_config(self):
        """Let us override settings withing plugins"""

        super(SuperdeskEve, self).load_config()
        self.config.from_object(superdesk)

abspath = os.path.abspath(os.path.dirname(__file__))
application = SuperdeskEve(data=superdesk.Superdesk, settings=os.path.join(abspath, 'settings.py'))

if __name__ == '__main__':
    application.run(debug=application.config.get('DEBUG'))
