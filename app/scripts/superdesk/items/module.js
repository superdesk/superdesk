define([
    'angular',
    'superdesk/items/controllers/list',
    'superdesk/items/resources'
], function(angular) {
    'use strict';

    angular.module('superdesk.items', ['superdesk.items.resources']).
        config(function($routeProvider) {
            $routeProvider.
                when('/', {
                    controller: require('superdesk/items/controllers/list'),
                    templateUrl: 'scripts/superdesk/items/views/list.html'
                });

        });
});
