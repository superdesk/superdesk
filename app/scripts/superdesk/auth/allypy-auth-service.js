define(['bower_components/jsSHA/src/sha512'], function(SHA) {
    'use strict';

    var AllyPyAuthAdapter = function($http, $q, config) {

        function url(uri) {
            return config.server.url + uri;
        }

        var HASH_TYPE = 'ASCII',
            HASH_ALGO = 'SHA-512',
            HASH_OUT = 'HEX';

        this.test = true;

        /**
         * Authenticate using given credentials
         *
         * @param {string} username
         * @param {string} password
         * @returns {object} promise
         */
        this.authenticate = function(username, password) {
            var defer = $q.defer(),
                reject = function(reason) {
                    console.log(reason);
                    defer.reject(reason);
                };

            getSessToken().then(function(token) {
                getAuthToken(token, username, password).then(function(session) {
                    $http.defaults.headers.common.Authorization = session.token;
                    defer.resolve(session);
                }, reject);
            }, reject);

            return defer.promise;
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
                return response.data;
            });
        }

        /**
         * Get session token for authentication
         *
         * @returns {object} promise
         */
        function getSessToken() {
            return $http.post(url('/Security/Authentication'), {
            }).then(function(response) {
                return response.data.Token;
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
    };

    AllyPyAuthAdapter.$inject = ['$http', '$q', 'config'];
    return AllyPyAuthAdapter;
});
