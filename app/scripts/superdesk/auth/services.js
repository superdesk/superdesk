define([
    'angular',
    'superdesk/api'
], function(angular) {
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

    angular.module('superdesk.auth.services', ['superdesk.api']).
        factory('Auth', function(resource) {
            return resource('/auth', {}, {
                save: {method: 'POST'}
            });
        }).
        service('authService', function($rootScope, $http, $q, Auth) {
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
                        console.log('ok', response);
                        self.setSessionData(response, rememberMe);
                        $rootScope.$broadcast('auth.login');
                        delay.resolve(response);
                    }, function(response) {
                        console.log('err', response);
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

            this.setSessionData = function (data, useLocalStorage) {
                data.user.isAnonymous = false;
                setItem('token', data.token, useLocalStorage);
                setItem('user', angular.toJson(data.user), useLocalStorage);
                initScope();
            };

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

            initScope();
        });
});
