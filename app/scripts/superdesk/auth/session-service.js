define(['lodash'], function(_) {
    'use strict';

    /**
     * Session Service stores current user data
     */
    SessionService.$inject = ['$q', '$rootScope', 'storage'];
    function SessionService($q, $rootScope, storage) {

        var TOKEN_KEY = 'sess:id',
            TOKEN_HREF = 'sess:href',
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
         * Update identity
         *
         * @param {object} updates
         * @returns {object} identity
         */
        this.updateIdentity = function(updates) {
            this.identity = this.identity || {};
            _.extend(this.identity, updates);
            storage.setItem(IDENTITY_KEY, this.identity);
        };

        /**
         * Start a new session
         *
         * @param {object} session
         * @param {object} identity
         */
        this.start = function(session, identity) {
            this.token = session.token;
            setToken(session.token);
            setSessionHref(session._links.self.href);

            this.identity = null;
            this.updateIdentity(identity);

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
            setSessionHref(null);
            storage.removeItem(IDENTITY_KEY);
        };

        /**
         * Return session url for delete
         *
         * @returns {string}
         */
        this.getSessionHref = function() {
            return localStorage.getItem(TOKEN_HREF);
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

        function setSessionHref(href) {
            if (href) {
                localStorage.setItem(TOKEN_HREF, href);
            } else {
                localStorage.removeItem(TOKEN_HREF);
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
