define(['lodash'], function(_) {
    'use strict';

    AuthService.$inject = ['$q', '$http', '$rootScope', 'storage', 'authAdapter'];
    function AuthService($q, $http, $rootScope, storage, authAdapter) {
        var defer;

        /**
         * current user identity
         */
        this.identity;
        initIdentity(this);

        /**
         * Get identity from stored auth token
         *
         * @returns {object} promise
         */
        this.getIdentity = function() {

            defer = defer ? defer : $q.defer();

            if (this.identity) {
                var promise = defer.promise;
                defer.resolve(this.identity);
                defer = null;
                return promise;
            }

            return defer.promise;
        };

        /**
         * Login using given credentials
         *
         * @param {string} username
         * @param {string} password
         * @returns {object} promise
         */
        this.login = function(username, password) {
            var auth = this;
            authAdapter.authenticate(username, password)
                .then(function(session) {
                    fetchIdentity(session).then(function(identity) {
                        storage.setItem('auth:token', session.Session);
                        storage.setItem('auth:identity', identity);
                        initIdentity(auth);
                        defer.resolve(identity);
                        defer = null;
                    }, rejectDefer);
                }, function(rsn) {
                    console.info('login failed', rsn);
                    rejectDefer;
                });

            return this.getIdentity();
        };

        /**
         * Logout
         */
        this.logout = function() {
            storage.removeItem('auth:token');
            storage.removeItem('auth:identity');
            this.identity = $rootScope.currentUser = null;
            delete $http.defaults.headers.common.Authorization;
            rejectDefer();
        };

        /**
         * Fetch user info for given session
         *
         * @param {object} session
         */
        function fetchIdentity(session) {
            return $http.get(session.User.href, {headers: {Authorization: session.Session}})
                .then(function(response) {
                    return response.data;
                });
        }

        /**
         * Init identity info from storage
         *
         * @param {Object} auth - auth service instance
         */
        function initIdentity(auth) {
            auth.identity = $rootScope.currentUser = storage.getItem('auth:identity');
            $http.defaults.headers.common.Authorization = storage.getItem('auth:token');
        }

        /**
         * Reject identity promise if exists
         */
        function rejectDefer() {
            if (defer) {
                defer.reject();
                defer = null;
            }
        }
    }

    return AuthService;
});
