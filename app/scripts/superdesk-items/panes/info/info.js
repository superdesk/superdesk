define([
    'angular'
], function(angular) {
    'use strict';

    angular.module('superdesk.panes.info', [])
        .config(['superdeskProvider', function(superdesk) {
            superdesk
                .pane('info', {
                    name: 'Info',
                    icon:'info',
                    template: 'scripts/superdesk-items/panes/info/pane.html',
                    position: 'right',
                    order: 0,
                    active: false,
                    selected: true
                });
        }])
        .controller('InfoPaneController', ['$scope', function ($scope) {

            $scope.removeTerm = function(arr, term) {
                arr.splice( _.find(arr,term),1);
            };

        }]);
});
