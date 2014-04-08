define([], function() {
    'use strict';

    AuthService.$inject = ['$http', '$q', 'session', 'authAdapter'];
    function AuthService($http, $q, session, authAdapter) {

        /**
         * Login using given credentials
         *
         * @param {string} username
         * @param {string} password
         * @returns {object} promise
         */
        this.login = function(username, password) {

            function fetchIdentity(loginData) {
                return $http.get(loginData.User.href, {headers: {Authorization: loginData.Session}})
                    .then(function(response) {
                        return response.data ? response.data : $q.reject(response);
                    });
            }

            return authAdapter.authenticate(username, password)
                .then(function(loginData) {
                    return fetchIdentity(loginData)
                        .then(function(userData) {
                            session.start(loginData, userData);
                            return session.identity;
                        });
                });
        };
    }

    return AuthService;
});
