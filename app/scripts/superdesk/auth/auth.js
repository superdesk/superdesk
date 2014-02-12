define(['angular', 'bower_components/jsSHA/src/sha512'], function(angular, SHA) {
    'use strict';

    var module = angular.module('superdesk.auth', []);

    module.service('auth', ['$http', '$q', function($http, $q) {

        var HASH_TYPE = 'ASCII',
            HASH_ALGO = 'SHA-512',
            HASH_OUT = 'HEX';

        /**
         * Login - get session token for given credentials
         *
         * @param {string} username
         * @param {string} password
         * @returns {object} promise
         */
        this.login = function(username, password) {
            var defer = $q.defer();

            getToken().then(function(token) {
                $http.post('/Security/Login', {
                    UserName: username,
                    Token: token,
                    HashedToken: signToken(token, username, password)
                }).then(function(response) {
                    // TODO set http auth header
                    defer.resolve(response.data);
                    return response.data;
                }, function() {
                    defer.reject();
                });
            }, function() {
                defer.reject();
            });

            return defer.promise;
        };

        /**
         * Get auth token for login
         *
         * @returns {object} promise
         */
        function getToken() {
            return $http.post('/Security/Authentication').then(function(response) {
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
    }]);
});
