define(['lodash'], function(_) {
    'use strict';

    /**
     * Session Service stores current user data
     */
    SessionService.$inject = ['$q', '$rootScope', 'storage'];
    function SessionService($q, $rootScope, storage) {

        var TOKEN_KEY = 'sess:id',
            IDENTITY_KEY = 'sess:user',
            defer;

        this.token = null;
        this.identity = null;

        /**
         * Get identity when available
         *
         * @returns {object} promise
         */
        this.getIdentity = function() {
            defer = defer ? defer : $q.defer();
            return defer.promise;
        };

        /**
         * Start a new session
         *
         * @param {string} token
         * @param {object} identity
         */
        this.start = function(token, identity) {
            this.token = token;
            this.identity = identity;

            setToken(token);
            storage.setItem(IDENTITY_KEY, identity);

            if (defer) {
                defer.resolve(identity);
                defer = null;
            }
        };

        /**
         * Set current session expired
         */
        this.expire = function() {
            this.token = null;
            setToken(null);
        };

        /**
         * Clear session info
         */
        this.clear = function() {
            this.expire();
            this.identity = null;
            storage.removeItem(IDENTITY_KEY);
        };

        $rootScope.$watch(getToken, _.bind(function(token) {
            this.token = token;
            this.identity = storage.getItem(IDENTITY_KEY);
        }, this));

        /**
         * Save token into local storage
         *
         * @param {string} token
         */
        function setToken(token) {
            if (token) {
                localStorage.setItem(TOKEN_KEY, token);
            } else {
                localStorage.removeItem(TOKEN_KEY);
            }
        }

        /**
         * Get token from local storage
         *
         * it's used via watch so it skips json serialization withing storage service
         *
         * @returns string
         */
        function getToken() {
            return localStorage.getItem(TOKEN_KEY) || null;
        }
    }

    return SessionService;
});
