define([
    'angular',
    'require',
    'angular-route',
    './auth-service',
    './allypy-auth-service',
    './login-modal-directive'
], function(angular, require) {
    'use strict';

    angular.module('superdesk.auth', ['superdesk', 'ngRoute'])
        .service('auth', require('./auth-service'))
        .service('authAdapter', require('./allypy-auth-service'))
        .directive('sdLoginModal', require('./login-modal-directive'))

        .controller('UserController', ['$scope', 'auth', function($scope, auth) {
            $scope.logout = function() {
                auth.logout();
            };
        }])

        /**
         * Stop route loading if there is no user identity
         */
        .run(['$rootScope', '$route', 'auth', function($rootScope, $route, auth) {
            $rootScope.$on('$locationChangeStart', function(e) {
                if (!auth.identity) {
                    auth.getIdentity().then(function(identity) {
                        $rootScope.identity = identity;
                        $route.reload();
                    });

                    e.preventDefault();
                }
            });
        }]);
});
