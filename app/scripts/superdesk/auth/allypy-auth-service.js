define(['bower_components/jsSHA/src/sha512'], function(SHA) {
    'use strict';

    AllyPyAuthAdapter.$inject = ['$http', '$q', 'config'];
    function AllyPyAuthAdapter($http, $q, config) {

        function url(uri) {
            return config.server.url + uri;
        }

        var HASH_TYPE = 'ASCII',
            HASH_ALGO = 'SHA-512',
            HASH_OUT = 'HEX';

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
            var secretKey = hmac(sha(hash(password)), username);
            return hmac(sha(token), secretKey);
        }

        /**
         * Get hmac for given sha obj and secret key
         *
         * @param {object} sha
         * @param {string} key
         * @returns {string}
         */
        function hmac(sha, key) {
            return sha.getHMAC(key, HASH_TYPE, HASH_ALGO, HASH_OUT);
        }

        /**
         * Get sha object for given string input
         *
         * @param {string} input
         * @returns {object}
         */
        function sha(input) {
            return new SHA(input, HASH_TYPE);
        }

        /**
         * Get hash of given input
         *
         * @param {string} input
         * @returns {string}
         */
        function hash(input) {
            return sha(input).getHash(HASH_ALGO, HASH_OUT);
        }
    }

    return AllyPyAuthAdapter;
});
