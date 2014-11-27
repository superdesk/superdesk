import logging
from flask import current_app as app, json
import superdesk
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
        superdesk.Option('--admin', '-a', dest='admin', required=False),
    )

    def run(self, username, password, email, admin='false'):

        # force type conversion to boolean
        is_admin = False if admin is None else json.loads(admin)
        user_type = 'administrator' if is_admin else 'user'

        userdata = {
            'username': username,
            'password': password,
            'email': email,
            'user_type': user_type,
            'is_active': is_admin,
            'needs_activation': not is_admin
        }

        with app.test_request_context('/users', method='POST'):
            if userdata.get('password', None) and not is_hashed(userdata.get('password')):
                userdata['password'] = get_hash(userdata.get('password'),
                                                app.config.get('BCRYPT_GENSALT_WORK_FACTOR', 12))

            user = superdesk.get_resource_service('users').find_one(username=userdata.get('username'), req=None)

            if user:
                logger.info('updating user %s' % (userdata))
                superdesk.get_resource_service('users').patch(user.get('_id'), userdata)
                return userdata
            else:
                logger.info('creating user %s' % (userdata))
                superdesk.get_resource_service('users').post([userdata])

            logger.info('user saved %s' % (userdata))
            return userdata


class HashUserPasswordsCommand(superdesk.Command):
    def run(self):
        users = superdesk.get_resource_service('auth_users').get(req=None, lookup={})
        for user in users:
            pwd = user.get('password')
            if not is_hashed(pwd):
                updates = {}
                hashed = get_hash(user['password'], app.config.get('BCRYPT_GENSALT_WORK_FACTOR', 12))
                user_id = user.get('_id')
                updates['password'] = hashed
                superdesk.get_resource_service('users').patch(user_id, updates=updates)


superdesk.command('users:create', CreateUserCommand())
superdesk.command('users:hash_passwords', HashUserPasswordsCommand())
