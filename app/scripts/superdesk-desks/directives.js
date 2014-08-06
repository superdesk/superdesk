define([
    'require',
    'lodash',
    'angular'
], function(require, _, angular) {
    'use strict';

    var app = angular.module('superdesk.desks.directives', []);
    app.directive('sdUserDesks', ['$rootScope', 'desks', function($rootScope, desks) {
        return {
            scope: {
                selectedDesk: '=desk'
            },
            templateUrl: require.toUrl('./views/user-desks.html'),
            link: function(scope, elem, attrs) {
                desks.fetchUserDesks($rootScope.currentUser).then(function(userDesks) {
                    scope.desks = userDesks._items;
                    scope.selectedDesk = _.find(scope.desks, {_id: desks.getCurrentDeskId()});
                });

                scope.select = function(desk) {
                    scope.selectedDesk = desk;
                    desks.setCurrentDesk(desk);
                };
            }
        };
    }]);
});
