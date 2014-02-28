define([], function() {
    'use strict';

    AuthService.$inject = ['session', '$http', 'authAdapter'];
    function AuthService(session, $http, authAdapter) {

        /**
         * Login using given credentials
         *
         * @param {string} username
         * @param {string} password
         * @returns {object} promise
         */
        this.login = function(username, password) {
            var token;

            function saveToken(loginData) {
                token = loginData.Session;
                return loginData;
            }

            function fetchIdentity(loginData) {
                return $http.get(loginData.User.href, {headers: {Authorization: loginData.Session}})
                    .then(function(response) {
                        return response.data;
                    });
            }

            function startSession(userData) {
                session.start(token, userData);
                return session.identity;
            }

            return authAdapter.authenticate(username, password)
                .then(saveToken)
                .then(fetchIdentity)
                .then(startSession);
        };
    }

    return AuthService;
});
