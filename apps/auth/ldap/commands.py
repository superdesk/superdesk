import logging
from flask import current_app as app
from apps.auth.errors import NotFoundAuthError
import superdesk
from .ldap import ADAuth
from superdesk.utc import utcnow


logger = logging.getLogger(__name__)


class ImportUserProfileFromADCommand(superdesk.Command):
    """
    Responsible for importing a user profile from Active Directory (AD) to Mongo.
    This command runs on assumption that the user executing this command and
    the user whose profile need to be imported need not to be the same. Uses ad_username and ad_password to bind to AD
    and then searches for a user identified by username_to_import and if found imports into Mongo.
    """

    option_list = (
        superdesk.Option('--ad_username', '-adu', dest='ad_username', required=True),
        superdesk.Option('--ad_password', '-adp', dest='ad_password', required=True),
        superdesk.Option('--username_to_import', '-u', dest='username', required=True),
    )

    def run(self, ad_username, ad_password, username):
        """
        Imports or Updates a User Profile from AD to Mongo.
        :param ad_username: Active Directory Username
        :param ad_password: Password of Active Directory Username
        :param username: Username as in Active Directory whose profile needs to be imported to Superdesk.
        :return: User Profile.
        """

        # Authenticate and fetch profile from AD
        settings = app.settings
        ad_auth = ADAuth(settings['LDAP_SERVER'], settings['LDAP_SERVER_PORT'], settings['LDAP_BASE_FILTER'],
                         settings['LDAP_USER_FILTER'], settings['LDAP_USER_ATTRIBUTES'], settings['LDAP_FQDN'])

        user_data = ad_auth.authenticate_and_fetch_profile(ad_username, ad_password, username)

        if len(user_data) == 0:
            raise NotFoundAuthError()

        # Check if User Profile already exists in Mongo
        user = superdesk.app.data.find_one('users', username=username, req=None)

        if user:
            user_data[app.config['LAST_UPDATED']] = utcnow()
            superdesk.apps['users'].update(user.get('_id'), user_data, trigger_events=False)
            return user_data
        else:
            user_data[app.config['DATE_CREATED']] = utcnow()
            user_data[app.config['LAST_UPDATED']] = utcnow()
            user_data['username'] = username
            superdesk.apps['users'].create([user_data], trigger_events=True)
            return user_data

superdesk.command('users:copyfromad', ImportUserProfileFromADCommand())
