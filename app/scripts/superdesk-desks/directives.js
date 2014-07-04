define([
    'require',
    'lodash',
    'angular'
], function(require, _, angular) {
    'use strict';

    var app = angular.module('superdesk.desks.directives', []);
    app.directive('sdUserDesks', ['desks', function(desks) {
        return {
            scope: {
                user: '=',
                selected: '=',
                select: '='
            },
            transclude: true,
            templateUrl: require.toUrl('./views/user-desks.html'),
            link: function(scope, elem, attrs) {
                scope.userDesks = null;
                scope.$watch('user', function(user) {
                    desks.fetchUserDesks(user)
                    .then(function(userDesks) {
                        scope.userDesks = userDesks;
                    });
                });

                scope._select = function(desk) {
                    if (typeof scope.select === 'function') {
                        scope.select(desk);
                    }
                };
            }
        };
    }])
    .directive('sdUserDesk', [function() {
        return {
            link: function(scope, element, attrs, controller, $transclude) {
                $transclude(scope, function(clone) {
                    element.empty();
                    element.append(clone);
                });
            }
        };
    }]);
});
