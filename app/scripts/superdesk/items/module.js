define([
    'angular',
    'angular-route',
    './controllers/list',
    './controllers/edit',
    './resources',
    './directives'
], function(angular) {
    'use strict';

    angular.module('superdesk.items', ['ngRoute', 'superdesk.items.resources', 'superdesk.items.directives']).
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
