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

    ResetPassworController.$inject = ['$scope', '$location'];
    function ResetPassworController($scope, $location) {
        $scope.flowStep = 1;

        $scope.isSending = false;
        $scope.sendToken = function() {
            console.log('send token to user email');
            var response = 200;
            if (response === 200) {
                $scope.flowStep = 2;
            }
        };

        $scope.isReseting = false;
        $scope.resetPassword = function() {
            console.log('password reset');
            var response = 200;
            if (response === 200) {
                $location.path('/');
            }
        };
    }

    return angular.module('superdesk.auth', [])
        .service('auth', require('./auth-service'))
        .service('session', require('./session-service'))
        .service('authAdapter', require('./basic-auth-adapter'))
        .directive('sdLoginModal', require('./login-modal-directive'))
        .config(['$httpProvider', 'superdeskProvider', function($httpProvider, superdesk) {
            $httpProvider.interceptors.push(AuthInterceptor);

            superdesk
                .activity('/reset-password/', {
                    controller: ResetPassworController,
                    templateUrl: require.toUrl('./reset-password.html'),
                    auth: false
                });
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
                    $http.defaults.headers.common.Authorization = token;
                } else {
                    delete $http.defaults.headers.common.Authorization;
                }
            });

            // prevent routing when there is no token
            $rootScope.$on('$locationChangeStart', function (e) {
                $rootScope.requiredLogin = $route.routes[$location.path()].auth;
                if (!session.token && $rootScope.requiredLogin) {
                    session.getIdentity().then(function() {
                        $http.defaults.headers.common.Authorization = session.token;
                        $route.reload();
                    });
                    e.preventDefault();
                }
            });
        }]);
});
