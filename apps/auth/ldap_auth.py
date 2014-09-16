import logging
from ldap3 import Connection, Server, STRATEGY_SYNC, AUTH_SIMPLE, SEARCH_SCOPE_WHOLE_SUBTREE, GET_ALL_INFO
from ldap3.core.exceptions import LDAPCommunicationError, LDAPBindError, LDAPExceptionError
from settings import LDAP_SERVER, LDAP_BASE_FILTER, LDAP_USER_FILTER, LDAP_USER_ATTRIBUTES

logger = logging.getLogger(__name__)

def login(user, password):
    """
    :param user: LDAP username
    :param password: LDAP password
    :return: user profile base on the LDAP_USER_ATTRIBUTES
    """
    try:
        s = Server(LDAP_SERVER, port = 389, get_info = GET_ALL_INFO)
        c = Connection(s, auto_bind = True, client_strategy = STRATEGY_SYNC, user=user,
                        password=password, authentication=AUTH_SIMPLE, check_names=True)

        base_filter = LDAP_BASE_FILTER
        user_filter = LDAP_USER_FILTER.format(user)
        logger.info('base filter:{} user filter:{}'.format(LDAP_BASE_FILTER, LDAP_USER_FILTER))

        with c:
            result = c.search(base_filter,user_filter, SEARCH_SCOPE_WHOLE_SUBTREE,
                     attributes = LDAP_USER_ATTRIBUTES)

            response = dict()

            if result:
                userProfile = c.response[0]['attributes']
                response['email'] = userProfile['mail'] if userProfile.__contains__('mail') else ''
                response['display_name'] = userProfile['displayName'] if userProfile.__contains__('displayName') else ''
                response['last_name'] = userProfile['sn'] if userProfile.__contains__('sn') else ''
                response['first_name'] = userProfile['givenName'] if userProfile.__contains__('givenName') else ''
                response['phone'] = userProfile['ipPhone'] if userProfile.__contains__('ipPhone') else ''
            else:
                logger.warning("Failed to login")

            return response
    #TODO: check what type of errors are thrown by the LDAP module
    # except LDAPBindError as bindEx:
    #     logger.error("Bind error occurred. Login failed for user {}.".format(user))
    # except LDAPExceptionError as ex:
    #     logger.error("LDAP Exception occurred. Login failed for user {}".format(user))
    # except LDAPCommunicationError as comEx:
    #     logger.error("Communication error occurred. Login failed for user {}".format(user))
    except Exception as e:
        logger.error("Exception occurred. Login failed for user {}".format(user))



#if __name__ == '__main__':
#    login('svc_bulletinsql','bulletinsql01')