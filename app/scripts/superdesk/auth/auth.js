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

    ResetPassworController.$inject = ['$scope', '$location', 'api', 'notify', 'gettext'];
    function ResetPassworController($scope, $location, api, notify, gettext) {
        $scope.isSending = false;
        $scope.isReseting = false;

        var resetForm = function() {
            $scope.email = '';
            $scope.token = '';
            $scope.password = '';
            $scope.passwordConfirm = '';
        };

        $scope.sendToken = function() {
        	$scope.sendTokenError = null;
            api.resetPassword.create({email: $scope.email})
            .then(function(result) {
                notify.success(gettext('Link sent. Please check your email inbox.'));
                $scope.flowStep = 2;
            }, function(rejection) {
            	$scope.sendTokenError = rejection.status;
            });
            resetForm();
        };
        $scope.resetPassword = function() {
        	$scope.setPasswordError = null;
            api.resetPassword.create({token: $scope.token, password: $scope.password})
            .then(function(result) {
                notify.success(gettext('Password is changed. You can login using your new password.'));
                $location.path('/').search({});
            }, function(rejection) {
            	$scope.setPasswordError = rejection.status;
            });
            resetForm();
        };

        resetForm();

        var query = $location.search();
        if (query.token) {
            $scope.token = query.token;
            $scope.flowStep = 3;
        } else {
            $scope.flowStep = 1;
        }
    }

    angular.module('superdesk.session', [])
        .service('session', require('./session-service'));

    return angular.module('superdesk.auth', ['superdesk.features', 'superdesk.activity', 'superdesk.session'])
        .service('auth', require('./auth-service'))
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
        .config(['apiProvider', function(apiProvider) {
            apiProvider.api('resetPassword', {
                type: 'http',
                backend: {
                    rel: 'reset_user_password'
                }
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
            $rootScope.$watch(function watchSessionIdentity() {
                return session.identity;
            }, function (identity) {
                $rootScope.currentUser = session.identity;
            });

            // set auth header
            $rootScope.$watch(function watchSessionToken() {
                return session.token;
            }, function(token) {
                if (token) {
                    $http.defaults.headers.common.Authorization = token;
                    $rootScope.sessionId = session.sessionId;
                } else {
                    delete $http.defaults.headers.common.Authorization;
                    $rootScope.sessionId = null;
                }
            });

            // prevent routing when there is no token
            $rootScope.$on('$locationChangeStart', function (e) {
                $rootScope.requiredLogin = requiresLogin($route.routes[$location.path()]);
                if (!session.token && $rootScope.requiredLogin) {
                    session.getIdentity().then(function() {
                        $http.defaults.headers.common.Authorization = session.token;
                    });
                    e.preventDefault();
                }
            });

            function requiresLogin(route) {
                return route ? route.auth : false;
            }
        }]);
});
