define([
    'angular'
], function(angular) {
    'use strict';

    return ['$rootScope', '$http', '$q', 'storage', 'em',
    function($rootScope, $http, $q, storage, em) {
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
            em.create('auth', {
                username: username,
                password: password
            }).then(function(response) {
                setSessionData(response, rememberMe);
                $rootScope.$broadcast('auth.login');
                delay.resolve(response);
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
            return !!this.getIdentity();
        };

        /**
         * Get current user identity
         *
         * @return {string}
         */
        this.getIdentity = function() {
            return storage.getItem('auth') ? storage.getItem('auth').user : false;
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
                em.find('users', authData.user).then(function(user) {
                    $rootScope.currentUser = angular.extend(user, {
                        isAnonymous: false
                    });
                });
            } else {
                $rootScope.currentUser = {
                    username: 'Anonymous',
                    isAnonymous: true
                };
            }
        }

        initScope();
    }];
});
