define(['angular'], function(angular) {
    'use strict';

    function prefixKey(key) {
        return 'superdesk.auth.' + key;
    }

    function getItem(key) {
        var escaped = sessionStorage.getItem(prefixKey(key));
        switch(escaped) {
            case 'undefined':
                return undefined;

            case 'null':
                return null;

            default:
                return escaped;
        }
    }

    function setItem(key, val, remember) {
        sessionStorage.setItem(prefixKey(key), val);
        if (remember) {
            localStorage.setItem(prefixKey(key), val);
        } else {
            localStorage.removeItem(prefixKey(key));
        }
    }

    return ['$rootScope', '$http', '$q', 'Auth', function($rootScope, $http, $q, Auth) {

        initScope();

        /**
         * Login
         *
         * @param {string} username
         * @param {string} password
         * @param {boolean} rememberMe
         */
        this.login = function(username, password, rememberMe) {
            var delay = $q.defer();

            if (!username || !password) {
                delay.reject();
                return delay.promise;
            }

            var self = this;
            Auth.save(
                {username: username, password: password},
                function(response) {
                    setSessionData(response, rememberMe);
                    $rootScope.$broadcast('auth.login');
                    delay.resolve(response);
                }, function(response) {
                    delay.reject(response);
                });

            return delay.promise;
        };

        /**
         * Logout
         */
        this.logout = function() {
            var keys = ['token', 'user'];
            angular.forEach(keys, function(key) {
                localStorage.removeItem(prefixKey(key));
                sessionStorage.removeItem(prefixKey(key));
            });

            initScope();
        };

        /**
         * Test if user is authenticated
         *
         * @return {boolean}
         */
        this.hasIdentity = function() {
            return !$rootScope.currentUser.isAnonymous;
        };

        function setSessionData(data, useLocalStorage) {
            data.user.isAnonymous = false;
            setItem('token', data.token, useLocalStorage);
            setItem('user', angular.toJson(data.user), useLocalStorage);
            initScope();
        }

        function setAuthenticationHeader(token) {
            if (token) {
                $http.defaults.headers.common.Authorization = 'Basic ' + btoa(token + ':');
            }
        }

        function initScope() {
            setAuthenticationHeader(getItem('token'));
            $rootScope.currentUser = angular.fromJson(getItem('user'));
            if (!$rootScope.currentUser) {
                $rootScope.currentUser = {
                    username: 'Anonymous',
                    isAnonymous: true
                }
            }
        }
    }];
});
