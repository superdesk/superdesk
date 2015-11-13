define(['lodash'], function(_) {
    'use strict';

    /**
     * Expire session on 401 server response
     */
    AuthExpiredInterceptor.$inject = ['session', '$q', '$injector', '$rootScope', 'config', 'lodash'];
    function AuthExpiredInterceptor(session, $q, $injector, $rootScope, config, _) {

        function handleAuthExpired(response) {
            session.expire();
            return session.getIdentity().then(function() {
                var $http = $injector.get('$http');
                $http.defaults.headers.common.Authorization = session.token;
                response.config.headers.Authorization = session.token;
                return $injector.get('request').resend(response.config);
            });
        }

        return {
            response: function(response) {
                if (_.startsWith(response.config.url, config.server.url) && response.status === 401) {
                    return handleAuthExpired(response);
                }

                return response;
            },
            responseError: function(response) {
                if (_.startsWith(response.config.url, config.server.url) && response.status === 401) {
                    if (!(((response.data || {})._issues || {}).credentials)) {
                        return handleAuthExpired(response);
                    }
                }

                return $q.reject(response);
            }
        };
    }

    return AuthExpiredInterceptor;
});
