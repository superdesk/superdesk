define([
    'angular',
    'angular-route',
    'bootstrap/dropdown',
    './controllers/list',
    './controllers/edit',
    './controllers/ref',
    './controllers/archive',
    './resources',
    './directives'
], function(angular) {
    'use strict';

    angular.module('superdesk.items', ['ngRoute', 'superdesk.items.resources', 'superdesk.items.directives']).
        config(function($routeProvider) {
            $routeProvider.
                when('/packages/:guid', {
                    templateUrl: 'scripts/superdesk/items/views/edit.html',
                    controller: require('superdesk/items/controllers/edit'),
                    resolve: {
                        item: function(ItemLoader) {
                            return ItemLoader();
                        }
                    }
                }).
                when('/items/', {
                    templateUrl: 'scripts/superdesk/items/views/archive.html',
                    controller: require('superdesk/items/controllers/archive'),
                    menu: {
                        parent: 'content',
                        label: 'Archive',
                        priority: -2
                    }
                }).
                when('/', {
                    controller: require('superdesk/items/controllers/list'),
                    templateUrl: 'scripts/superdesk/items/views/list.html',
                    menu: {
                        parent: 'content',
                        label: 'Packages',
                        priority: -1
                    }
                });
        }).
        run(function($rootScope) {
            $rootScope.mode = {
                zen: false
            };
        }).
        controller('RefController', require('superdesk/items/controllers/ref'));
});
