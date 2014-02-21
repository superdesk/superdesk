define(['lodash'], function(_) {
    'use strict';

    var AuthService = function($q, $http, storage, authAdapter) {

        var TOKEN_KEY = 'auth:token',
            USER_KEY = 'auth:user',
            defer;

        /**
         * current user identity
         */
        this.identity = null;

        /**
         * Get identity from stored auth token
         *
         * @returns {object} promise
         */
        this.getIdentity = function() {

            // return existing promise
            if (defer) {
                return defer.promise;
            }

            defer = $q.defer();
            if (this.identity) {
                var promise = defer.promise;
                defer.resolve(this.identity);
                defer = null;
                return promise;
            }

            loadIdentity();

            // set this.identity when resolved
            return defer.promise.then(_.bind(function(identity) {
                this.identity = identity;
                return this.identity;
            }, this));
        };

        /**
         * Login using given credentials
         *
         * @param {string} username
         * @param {string} password
         * @param {boolean} rememberMe
         */
        this.login = function(username, password, rememberMe) {
            authAdapter.authenticate(username, password)
                .then(_.bind(function(session) {
                    saveIdentity(session, rememberMe);
                    loadIdentity();
                }, this), _.bind(function(rsn) {
                    console.info('login failed', rsn);
                    this.logout();
                }, this));

            return this.getIdentity();
        };

        /**
         * Logout
         */
        this.logout = function() {
            storage.removeItem(TOKEN_KEY);
            storage.removeItem(USER_KEY);
            this.identity = null;
            if (defer) {
                defer.reject();
                defer = null;
            }
        };

        /**
         * Load stored identity (if such exists)
         */
        function loadIdentity() {
            var token = storage.getItem(TOKEN_KEY),
                userHref = storage.getItem(USER_KEY);

            if (token && userHref) {
                $http.defaults.headers.common.Authorization = token;
                $http.get(userHref)
                    .then(function(response) {
                        defer.resolve(response.data);
                        defer = null;
                    }, function(info) {
                        defer.reject(info);
                        defer = null;
                    });
            }
        }

        /**
         * Save identity info for loading
         */
        function saveIdentity(identity, useLocalStorage) {
            storage.setItem(TOKEN_KEY, identity.Session, useLocalStorage);
            storage.setItem(USER_KEY, identity.User.href, useLocalStorage);
        }
    };

    AuthService.$inject = ['$q', '$http', 'storage', 'authAdapter'];
    return AuthService;
});
