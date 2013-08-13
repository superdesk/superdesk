define([
    'angular',
    'jquery',
    'bootstrap/bootstrap-modal',
    'superdesk/auth/services'
], function(angular, $) {
    'use strict';

    angular.module('superdesk.auth.directives', ['superdesk.auth.services']).
        directive('sdLoginModal', function($rootScope, authService) {
            return {
                restrict: 'A',
                replace: true,
                scope: {},
                templateUrl: 'scripts/superdesk/auth/views/login.html',
                link: function($scope, element, attrs) {
                    $(element).modal({
                        keyboard: false,
                        show: !authService.hasIdentity()
                    });

                    $scope.doLogin = function() {
                        authService.login($scope.username, $scope.password, $scope.rememberMe).
                            then(function() {
                                $scope.password = null;
                                $scope.loginError = false;
                                $(element).modal('hide');
                            }, function() {
                                $scope.password = null;
                                $scope.loginError = true;
                            });
                    };

                    $rootScope.$on('auth.doLogin', function(event) {
                        $(element).modal('show');
                    });
                }
            };
        });
});
