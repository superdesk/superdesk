define([], function() {
    'use strict';

    AuthService.$inject = ['$q', 'api', 'session', 'authAdapter'];
    function AuthService($q, api, session, authAdapter) {

        /**
         * Login using given credentials
         *
         * @param {string} username
         * @param {string} password
         * @returns {object} promise
         */
        this.login = function(username, password) {

            function fetchIdentity(loginData) {
                return api.users.getById(loginData.user);
            }

            return authAdapter.authenticate(username, password)
                .then(function(sessionData) {
                    return fetchIdentity(sessionData)
                        .then(function(userData) {
                            session.start(sessionData, userData);
                            return session.identity;
                        });
                });
        };
    }

    return AuthService;
});
