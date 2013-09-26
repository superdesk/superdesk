define([
    'angular',
    'angular-route',
    'bootstrap/dropdown',
    './controllers/list',
    './controllers/edit',
    './controllers/ref',
    './resources',
    './directives'
], function(angular) {
    'use strict';

    angular.module('superdesk.items', ['ngRoute', 'superdesk.items.resources', 'superdesk.items.directives']).
        config(function($routeProvider) {

            function getItemLoader(defaultParams) {
                return function($route, ItemListLoader) {
                    var params = angular.extend({
                        sort: '[("firstCreated", -1)]',
                        skip: 0,
                        limit: 25
                    }, defaultParams, $route.current.params);
                    return ItemListLoader(params);
                };
            }

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
                when('/archive/', {
                    templateUrl: 'scripts/superdesk/items/views/archive.html',
                    controller: require('superdesk/items/controllers/list'),
                    resolve: {
                        items: ['ItemListLoader', function(ItemListLoader) {
                            return ItemListLoader({itemClass: 'icls:picture,icls:text'});
                        }]
                    },
                    menu: {
                        parent: 'content',
                        label: 'Archive',
                        priority: -2
                    }
                }).
                when('/items/', {
                    controller: require('superdesk/items/controllers/list'),
                    templateUrl: 'scripts/superdesk/items/views/list.html',
                    resolve: {
                        items: ['ItemListLoader', function(ItemListLoader) {
                            return ItemListLoader({itemClass: 'icls:composite'});
                        }]
                    },
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
