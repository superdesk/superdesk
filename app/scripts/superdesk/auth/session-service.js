define(['lodash'], function(_) {
    'use strict';

    /**
     * Session Service stores current user data
     */
    SessionService.$inject = ['$q', '$rootScope', 'storage', 'preferencesService'];
    function SessionService($q, $rootScope, storage, preferencesService) {

        var TOKEN_KEY = 'sess:token',
            TOKEN_HREF = 'sess:href',
            IDENTITY_KEY = 'sess:user',
            SESSION_ID = 'sess:id',
            defer;

        this.token = null;
        this.identity = null;
        this.sessionId = null;

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
            this.sessionId = session._id;
            setToken(session.token);
            setSessionId(session._id);
            setSessionHref(session._links.self.href);

            this.identity = null;
            this.updateIdentity(identity);

            preferencesService.getPreferences(session._id).then(function(preferences) {
                    preferencesService.saveLocally(preferences);

                    if (defer) {
                        defer.resolve(identity);
                        defer = null;
                    }
            });
        };

        /**
         * Start a mock session for given user id
         *
         * @param {string} userId
         */
        this.mock = function(userId) {
            return this.start({
                _links: {self: {href: null}},
                token: 'token'
            }, {
                _id: userId,
                username: 'foo'
            });
        };

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
            storage.removeItem(IDENTITY_KEY);
            preferencesService.deleteLocally();
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
            this.sessionId = localStorage.getItem(SESSION_ID);
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
