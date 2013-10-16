define([
    'angular',
    'angular-route',
    'bootstrap_ui',
    './controllers/list',
    './controllers/edit',
    './controllers/ref',
    './resources',
    './directives'
], function(angular) {
    'use strict';

    angular.module('superdesk.items', ['ngRoute', 'superdesk.items.resources', 'superdesk.items.directives','ui.bootstrap.dropdownToggle']).
        config(function($routeProvider) {

            $routeProvider.
                when('/packages/:id', {
                    templateUrl: 'scripts/superdesk/items/views/edit.html',
                    controller: require('superdesk/items/controllers/edit'),
                    resolve: {
                        item: ['itemLoader', function(itemLoader) {
                            return itemLoader();
                        }]
                    }
                }).
                when('/archive/', {
                    templateUrl: 'scripts/superdesk/items/views/archive.html',
                    controller: require('superdesk/items/controllers/list'),
                    resolve: {
                        items: ['itemListLoader', function(itemListLoader) {
                            return itemListLoader({itemClass: 'icls:picture'});
                        }]
                    },
                    menu: {
                        parent: 'content',
                        label: gettext('Archive'),
                        priority: -2
                    }
                }).
                when('/items/', {
                    controller: require('superdesk/items/controllers/list'),
                    templateUrl: 'scripts/superdesk/items/views/list.html',
                    resolve: {
                        items: ['itemListLoader', function(itemListLoader) {
                            return itemListLoader({itemClass: 'icls:composite'});
                        }]
                    },
                    menu: {
                        parent: 'content',
                        label: gettext('Packages'),
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
