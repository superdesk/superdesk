from superdesk import app
from datetime import timedelta
from superdesk.utc import utcnow
from eve.utils import date_to_str


class RemoveExpiredSessions():

    def run(self):
        self.remove_expired_sessions()

    def remove_expired_sessions(self):
        expiry_minutes = app.settings['SESSION_EXPIRY_MINUTES']
        expiration_time = utcnow() - timedelta(minutes=expiry_minutes)
        print('Deleting session not updated since {}'.format(expiration_time))
        query = {'_updated': {'$lte': date_to_str(expiration_time)}}
        app.data.remove('auth', query)
