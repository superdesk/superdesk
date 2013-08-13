define(['angular', 'angular-resource', 'superdesk/auth/services'], function(angular) {
    'use strict';

    angular.module('superdesk.menu', ['ngResource', 'superdesk.auth.services']).
        factory('Actions', function($resource) {
            return $resource('/resources/my/GUI/Action', {}, {
                query: {method: 'GET', isArray: false}
            });
        }).
        factory('MenuLoader', function($q, Actions) {
            return function() {
                var delay = $q.defer();
                var actions = [];
                Actions.query({path: 'menu.*'}, function(response) {
                    actions = response.ActionList;
                    Actions.query({path: 'menu.*.*'}, function(response) {
                        angular.forEach(actions, function(action) {
                            action.subactions = [];
                            angular.forEach(response.ActionList, function(subaction) {
                                if (subaction.Path.indexOf(action.Path) === 0) {
                                    action.subactions.push(subaction);
                                }
                            });
                        });

                        delay.resolve(actions);
                    });
                });

                return delay.promise;
            };
        }).
        controller('NavController', ['$scope', 'authService', 'MenuLoader', function($scope, authService, MenuLoader) {
            $scope.templateUrl = '/content/lib/core/templates/navbar.html';

            $scope.logout = function() {
                authService.logout();
            };

            $scope.$watch('currentUser', function(currentUser) {
                if (currentUser.Id) {
                    $scope.actions = MenuLoader()
                } else {
                    $scope.actions = [];
                }
            });
        }]);
});
