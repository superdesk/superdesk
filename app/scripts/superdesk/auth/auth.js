define([
    'angular',
    'require',
    'angular-route',
    './auth-service',
    './session-service',
    './allypy-auth-service',
    './login-modal-directive'
], function(angular, require) {
    'use strict';

    angular.module('superdesk.auth', ['superdesk', 'ngRoute'])
        .service('auth', require('./auth-service'))
        .service('session', require('./session-service'))
        .service('authAdapter', require('./allypy-auth-service'))
        .directive('sdLoginModal', require('./login-modal-directive'))

        /**
         * Intercept $http response errors and do login on 401
         */
        .config(['$httpProvider', function($httpProvider) {
            $httpProvider.interceptors.push(function(session, $injector) {
                return {
                    responseError: function(rejection) {
                        if (rejection.status === 401) {
                            session.expire();
                            return session.getIdentity().then(function() {
                                var $http = $injector.get('$http');
                                $http.defaults.headers.common.Authorization = session.token;
                                rejection.config.headers.Authorization = session.token;
                                return $http(rejection.config);
                            });
                        }
                    }
                };
            });
        }])

        // set root scope identity
        .run(['$rootScope', 'session', function($rootScope, session) {
            $rootScope.logout = function() {
                session.expire();
            };

            $rootScope.$watch(function() {
                return session.identity;
            }, function (identity) {
                $rootScope.currentUser = session.identity;
            });
        }])

        // wait with route loading until we have auth token
        .run(['$rootScope', '$route', '$http', 'session', function($rootScope, $route, $http, session) {
            $rootScope.$on('$locationChangeStart', function (e) {
                if (!session.token) {
                    session.getIdentity().then(function() {
                        $http.defaults.headers.common.Authorization = session.token;
                        $route.reload();
                    });
                    e.preventDefault();
                }
            });
        }]);
});
