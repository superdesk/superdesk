import logging
from flask import current_app as app
import superdesk
from superdesk.utc import utcnow
from superdesk.utils import get_hash, is_hashed


logger = logging.getLogger(__name__)


class CreateUserCommand(superdesk.Command):
    """Create a user with given username, password and email.
    If user with given username exists, reset password.
    """

    option_list = (
        superdesk.Option('--username', '-u', dest='username', required=True),
        superdesk.Option('--password', '-p', dest='password', required=True),
        superdesk.Option('--email', '-e', dest='email', required=True),
    )

    def run(self, username, password, email):

        userdata = {
            'username': username,
            'password': password,
            'email': email,
            app.config['LAST_UPDATED']: utcnow(),
        }

        with app.test_request_context('/users', method='POST'):
            if userdata.get('password', None) and not is_hashed(userdata.get('password')):
                userdata['password'] = get_hash(userdata.get('password'),
                                                app.config.get('BCRYPT_GENSALT_WORK_FACTOR', 12))

            user = app.data.find_one('users', username=userdata.get('username'), req=None)

            if user:
                logger.info('updating user %s' % (userdata))
                app.data.update('users', user.get('_id'), userdata)
                return userdata
            else:
                logger.info('creating user %s' % (userdata))
                userdata[app.config['DATE_CREATED']] = userdata[app.config['LAST_UPDATED']]
                app.data.insert('users', [userdata])

            logger.info('user saved %s' % (userdata))
            return userdata


class HashUserPasswordsCommand(superdesk.Command):
    def run(self):
        users = superdesk.app.data.find_all('auth_users')
        for user in users:
            pwd = user.get('password')
            if not is_hashed(pwd):
                updates = {}
                hashed = get_hash(user['password'], app.config.get('BCRYPT_GENSALT_WORK_FACTOR', 12))
                user_id = user.get('_id')
                updates['password'] = hashed
                superdesk.app.data.update('users', user_id, updates=updates)


superdesk.command('users:create', CreateUserCommand())
superdesk.command('users:hash_passwords', HashUserPasswordsCommand())
