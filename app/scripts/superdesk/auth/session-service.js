define([], function() {
    'use strict';

    /**
     * Session Service stores current user data
     */
    SessionService.$inject = ['$q', 'storage'];
    function SessionService($q, storage) {

        var TOKEN_KEY = 'sess:id',
            IDENTITY_KEY = 'sess:user',
            defer;

        this.token = sessionStorage.getItem(TOKEN_KEY);
        this.identity = storage.getItem(IDENTITY_KEY);

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

            sessionStorage.setItem(TOKEN_KEY, token);
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
            sessionStorage.removeItem(TOKEN_KEY);
        };

        /**
         * Clear session info
         */
        this.clear = function() {
            this.expire();
            this.identity = null;
            storage.removeItem(IDENTITY_KEY);
        };
    }

    return SessionService;
});
