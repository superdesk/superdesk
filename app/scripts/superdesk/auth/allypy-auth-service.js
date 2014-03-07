define(['superdesk/hashlib'], function(hashlib) {
    'use strict';

    AllyPyAuthAdapter.$inject = ['$http', '$q', 'config'];
    function AllyPyAuthAdapter($http, $q, config) {

        function url(uri) {
            return config.server.url + uri;
        }

        /**
         * Authenticate using given credentials
         *
         * @param {string} username
         * @param {string} password
         * @returns {object} promise
         */
        this.authenticate = function(username, password) {
            return getSessToken()
                .then(function(token) {
                    return getAuthToken(token, username, password);
                });
        };

        /**
         * Get authentication token used for following requests
         *
         * @param {string} token
         * @param {string} username
         * @param {string} password
         * @returns {object} promise
         */
        function getAuthToken(token, username, password) {
            return $http.post(url('/Security/Login'), {
                UserName: username,
                Token: token,
                HashedToken: signToken(token, username, password)
            }).then(function(response) {
                return response.data.Session ? response.data : $q.reject(response);
            });
        }

        /**
         * Get session token for authentication
         *
         * @returns {object} promise
         */
        function getSessToken() {
            return $http.post(url('/Security/Authentication'))
                .then(function(response) {
                    return response.data.Token ? response.data.Token : $q.reject(response);
                });
        }

        /**
         * Sign given token using user credentials
         *
         * @param {string} token
         * @param {string} username
         * @param {string} password
         * @returns {string}
         */
        function signToken(token, username, password) {
            var secretKey = hashlib.hmac(hashlib.hash(password), username);
            return hashlib.hmac(token, secretKey);
        }
    }

    return AllyPyAuthAdapter;
});
