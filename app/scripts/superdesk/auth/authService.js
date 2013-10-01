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
                {auth: {username: username, password: password}},
                function(response) {
                    setSessionData(response.auth, rememberMe);
                    $rootScope.$broadcast('auth.login');
                    delay.resolve(response.auth);
                }, function(response) {
                    self.logout();
                    delay.reject(response);
                });

            return delay.promise;
        };

        /**
         * Logout
         */
        this.logout = function() {
            storage.removeItem('auth');
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
            data.isAnonymous = false;
            storage.setItem('auth', data, useLocalStorage);
            initScope();
        }

        function setAuthenticationHeader(token) {
            if (token) {
                $http.defaults.headers.common.Authorization = 'Basic ' + btoa(token + ':');
            }
        }

        function initScope() {
            var authData = storage.getItem('auth');
            if (authData) {
                setAuthenticationHeader(authData.token);
                $rootScope.currentUser = angular.extend(authData, {
                    isAnonymous: false
                });
            } else {
                $rootScope.currentUser = {
                    username: 'Anonymous',
                    isAnonymous: true
                }
            }
        }
    }];
});
