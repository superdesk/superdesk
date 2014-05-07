define([
    'angular',
    'require',
    './auth-interceptor',
    './auth-service',
    './session-service',
    './basic-auth-adapter',
    './login-modal-directive'
], function(angular, require, AuthInterceptor) {
    'use strict';

    return angular.module('superdesk.auth', [])
        .service('auth', require('./auth-service'))
        .service('session', require('./session-service'))
        .service('authAdapter', require('./basic-auth-adapter'))
        .directive('sdLoginModal', require('./login-modal-directive'))
        .config(['$httpProvider', function($httpProvider) {
            $httpProvider.interceptors.push(AuthInterceptor);
        }])

        // watch session token, identity
        .run(['$rootScope', '$route', '$location', '$http', '$window', 'session',
        function($rootScope, $route, $location, $http, $window, session) {

            $rootScope.logout = function() {

                function replace() {
                    session.clear();
                    $window.location.replace('/'); // reset page for new user
                }

                var sessionHref = session.getSessionHref();
                if (sessionHref) {
                    $http['delete'](sessionHref).then(replace, replace);
                } else {
                    replace();
                }
            };

            // populate current user
            $rootScope.$watch(function() {
                return session.identity;
            }, function (identity) {
                $rootScope.currentUser = session.identity;
            });

            // set auth header
            $rootScope.$watch(function() {
                return session.token;
            }, function(token) {
                if (token) {
                    $http.defaults.headers.common.Authorization = 'Basic ' + btoa(token + ':');
                } else {
                    delete $http.defaults.headers.common.Authorization;
                }
            });

            // prevent routing when there is no token
            $rootScope.$on('$locationChangeStart', function (e) {
                if (!session.token) {
                    session.getIdentity().then(function() {
                        $http.defaults.headers.common.Authorization = 'Basic ' + btoa(session.token + ':');
                        $route.reload();
                    });
                    e.preventDefault();
                }
            });
        }]);
});
