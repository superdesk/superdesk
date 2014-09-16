import logging
from ldap3 import Connection, Server, STRATEGY_SYNC, AUTH_SIMPLE, SEARCH_SCOPE_WHOLE_SUBTREE, GET_ALL_INFO
from ldap3.core.exceptions import LDAPCommunicationError, LDAPBindError, LDAPExceptionError
from settings import LDAP_SERVER, LDAP_BASE_FILTER, LDAP_USER_FILTER, LDAP_USER_ATTRIBUTES

logger = logging.getLogger(__name__)


def authenticate_and_fetch_profile(username, password, username_for_profile=None):
    """
    Authenticates a user with credentials username and password against AD. If authentication is successful then it
    fetches a profile of a user identified by username_for_profile and if found the profile is returned.
    :param username: LDAP username
    :param password: LDAP password
    :param username_for_profile: Username of the profile to be fetched
    :return: user profile base on the LDAP_USER_ATTRIBUTES
    """

    if username_for_profile is None:
        username_for_profile = username

    try:
        s = Server(LDAP_SERVER, port=389, get_info=GET_ALL_INFO)
        c = Connection(s, auto_bind=True, client_strategy=STRATEGY_SYNC, user=username,
                       password=password, authentication=AUTH_SIMPLE, check_names=True)

        base_filter = LDAP_BASE_FILTER
        user_filter = LDAP_USER_FILTER.format(username_for_profile)
        logger.info('base filter:{} user filter:{}'.format(LDAP_BASE_FILTER, LDAP_USER_FILTER))

        with c:
            result = c.search(base_filter, user_filter, SEARCH_SCOPE_WHOLE_SUBTREE,
                              attributes=LDAP_USER_ATTRIBUTES)

            response = dict()

            if result:
                user_profile = c.response[0]['attributes']
                response['email'] = user_profile['mail'] if user_profile.__contains__('mail') else ''
                response['display_name'] = user_profile['displayName'] if user_profile.__contains__('displayName') else ''
                response['last_name'] = user_profile['sn'] if user_profile.__contains__('sn') else ''
                response['first_name'] = user_profile['givenName'] if user_profile.__contains__('givenName') else ''
                response['phone'] = user_profile['ipPhone'] if user_profile.__contains__('ipPhone') else ''
            else:
                logger.warning("Failed to login")

            return response
    # TODO: check what type of errors are thrown by the LDAP module
    # except LDAPBindError as bindEx:
    #     logger.error("Bind error occurred. Login failed for user {}.".format(user))
    # except LDAPExceptionError as ex:
    #     logger.error("LDAP Exception occurred. Login failed for user {}".format(user))
    # except LDAPCommunicationError as comEx:
    #     logger.error("Communication error occurred. Login failed for user {}".format(user))
    except Exception as e:
        logger.error("Exception occurred. Login failed for user {}".format(username))



        #if __name__ == '__main__':
        #    login('svc_bulletinsql','bulletinsql01')