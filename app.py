
import eve
from superdesk import Superdesk

application = eve.Eve(data=Superdesk, settings='settings.py')

if __name__ == '__main__':
    application.run(debug=application.config.get('DEBUG'))
