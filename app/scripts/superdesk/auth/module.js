define([
    'angular',
    'angular-route',
    'superdesk/auth/directives',
    'superdesk/auth/services',
    'superdesk/storage'
], function(angular) {
    'use strict';

    angular.module('superdesk.auth', ['ngRoute', 'superdesk.auth.directives', 'superdesk.auth.services', 'superdesk.storage']).
        run(function($rootScope, $route, authService) {
            $rootScope.$on('$locationChangeStart', function(event, url) {
                if (!authService.hasIdentity()) {
                    event.preventDefault();
                    $rootScope.$broadcast('auth.doLogin');
                }
            });

            $rootScope.$on('auth.login', function() {
                $route.reload();
            });
        }).
        controller('UserController', ['$scope', 'authService', function($scope, authService) {
            $scope.logout = function() {
                authService.logout();
                $scope.$emit('auth.doLogin');
            };
        }]);
});
