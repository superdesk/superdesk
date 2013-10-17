define([
    'angular',
    'superdesk/server',
    'superdesk/entity',
    'bootstrap_ui',
    './resources',
    './controllers/list',
    './controllers/edit',
    './controllers/ref',
    './directives'
], function(angular) {
    'use strict';

    angular.module('superdesk.items', ['superdesk.entity', 'superdesk.items.resources', 'superdesk.items.directives', 'ui.bootstrap.dropdownToggle'])
        .config(function($routeProvider) {
            $routeProvider.
                when('/packages/:id', {
                    templateUrl: 'scripts/superdesk/items/views/edit.html',
                    controller: require('superdesk/items/controllers/edit'),
                    resolve: {
                        item: ['$route', 'server', function($route, server) {
                            return server.readById('items', $route.current.params.id);
                        }]
                    }
                }).
                when('/archive/', {
                    templateUrl: 'scripts/superdesk/items/views/archive.html',
                    controller: require('superdesk/items/controllers/list'),
                    resolve: {
                        items: ['$route', 'Criteria', 'em', function($route, Criteria, em) {
                            var criteria = new Criteria({
                                itemClass: 'icls:composite',
                                sort: '[("firstCreated", -1)]',
                                max_results: 25
                            }, $route.current.params);
                            return em.getRepository('items').matching(criteria);
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
                        items: ['$route', 'Criteria', 'em', function($route, Criteria, em) {
                            var criteria = new Criteria({
                                itemClass: 'icls:text',
                                sort: '[("versionCreated", -1)]',
                                max_results: 25
                            }, $route.current.params);
                            return em.getRepository('items').matching(criteria);
                        }]
                    },
                    menu: {
                        parent: 'content',
                        label: gettext('Packages'),
                        priority: -1
                    }
                });
        })
        .run(function($rootScope) {
            // todo(petr) - remove from root scope, directive maybe?
            $rootScope.mode = {
                zen: false
            };
        })
        .controller('RefController', require('superdesk/items/controllers/ref'));

});
