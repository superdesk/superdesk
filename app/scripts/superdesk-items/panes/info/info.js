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
                    active: false,
                    selected: true
                });
        }])
        .controller('InfoPaneController', ['$scope', function ($scope) {
            //pane controller code
    }]);
});
