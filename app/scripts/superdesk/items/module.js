define([
    'angular',
    './controllers/list',
    './controllers/edit',
    './resources',
    './filters'
], function(angular) {
    'use strict';

    angular.module('superdesk.items', ['superdesk.items.resources', 'superdesk.items.filters']).
        config(function($routeProvider) {
            $routeProvider.
                when('/items/:guid', {
                    templateUrl: 'scripts/superdesk/items/views/edit.html',
                    controller: require('superdesk/items/controllers/edit'),
                    resolve: {
                        item: function(ItemLoader) {
                            return ItemLoader();
                        }
                    }
                }).
                when('/', {
                    controller: require('superdesk/items/controllers/list'),
                    templateUrl: 'scripts/superdesk/items/views/list.html'
                });

        });
});
