define([
    'angular'
], function(angular) {
    'use strict';

    return ['$rootScope', '$http', '$q', 'Auth', 'storage',
    function($rootScope, $http, $q, Auth, storage) {
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
            var keys = ['auth:token', 'auth:user'];
            angular.forEach(keys, function(key) {
                storage.removeItem(key);
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
            storage.setItem('auth:token', data.token, useLocalStorage);
            storage.setItem('auth:user', data.user, useLocalStorage);
            initScope();
        }

        function setAuthenticationHeader(token) {
            if (token) {
                $http.defaults.headers.common.Authorization = 'Basic ' + btoa(token + ':');
            }
        }

        function initScope() {
            setAuthenticationHeader(storage.getItem('auth:token'));
            $rootScope.currentUser = storage.getItem('auth:user');
            if (!$rootScope.currentUser) {
                $rootScope.currentUser = {
                    username: 'Anonymous',
                    isAnonymous: true
                }
            }
        }
    }];
});
