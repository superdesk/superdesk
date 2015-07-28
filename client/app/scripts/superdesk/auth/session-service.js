define(['lodash'], function(_) {
    'use strict';

    /**
     * Session Service stores current user data
     */
    SessionService.$inject = ['$q', '$rootScope', 'storage'];
    function SessionService($q, $rootScope, storage) {

        var TOKEN_KEY = 'sess:token';
        var TOKEN_HREF = 'sess:href';
        var IDENTITY_KEY = 'sess:user';
        var SESSION_ID = 'sess:id';
        var IDENTITY_BLACKLIST = [
            'session_preferences',
            'user_preferences',
            'allowed_actions',
            'workspace'
        ];
        var defer;

        this.token = null;
        this.identity = null;
        this.sessionId = null;

        /**
         * Get identity when available
         *
         * @returns {object} promise
         */
        this.getIdentity = function() {
            if (this.identity && this.token) {
                return $q.when(this.identity);
            }

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
            var identity = this.identity || {};
            _.extend(identity, updates);
            this.identity = _.omit(identity, IDENTITY_BLACKLIST);
            storage.setItem(IDENTITY_KEY, this.identity);
            return this.identity;
        };

        /**
         * Start a new session
         *
         * @param {object} session
         * @param {object} identity
         */
        this.start = function(session, identity) {
            this.token = session.token;
            this.sessionId = session._id;
            setToken(session.token);
            setSessionId(session._id);
            setSessionHref(session._links && session._links.self.href);

            this.identity = null;
            resolveIdentity(this.updateIdentity(identity));
        };

        function resolveIdentity(identity) {
            if (defer) {
                defer.resolve(identity);
                defer = null;
            }
        }

        /**
         * Set current session expired
         */
        this.expire = function() {
            this.token = null;
            this.sessionId = null;
            setToken(null);
            setSessionId(null);
        };

        /**
         * Clear session info
         */
        this.clear = function() {
            this.expire();
            this.identity = null;
            setSessionHref(null);
            setSessionId(null);
            storage.clear();
        };

        /**
         * Return session url for delete
         *
         * @returns {string}
         */
        this.getSessionHref = function() {
            return localStorage.getItem(TOKEN_HREF);
        };

        /**
         * Setup test user with given id.
         *
         * @param {string} _id
         */
        this.testUser = function(_id) {
            this.token = 1;
            this.identity = {_id: _id};
            this.sessionId = 's' + _id;
        };

        $rootScope.$watch(getToken, angular.bind(this, function(token) {
            this.token = token;
            this.identity = storage.getItem(IDENTITY_KEY);
            this.sessionId = localStorage.getItem(SESSION_ID);
            if (this.identity && this.token) {
                resolveIdentity(this.identity);
            }
        }));

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
         * Save session id into local storage
         *
         * @param {string} sessionId
         */
        function setSessionId(sessionId) {
            if (sessionId) {
                localStorage.setItem(SESSION_ID, sessionId);
            } else {
                localStorage.removeItem(SESSION_ID);
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
