define([
    'jquery',
    'angular',
    'superdesk/server',
    'superdesk/entity',
    'bootstrap_ui',
    './resources',
    './controllers/list',
    './controllers/edit',
    './controllers/ref',
    './controllers/settings',
    './directives'
], function($, angular) {
    'use strict';

    angular.module('superdesk.items', [
        'superdesk.entity',
        'superdesk.items.resources',
        'superdesk.items.directives',
        'ui.bootstrap'
    ])
        .controller('SettingsCtrl', require('superdesk/items/controllers/settings'))
        .controller('RefController', require('superdesk/items/controllers/ref'))
        .factory('providerRepository', ['em', function(em) {
            var repository = em.getRepository('ingest_providers');
            return repository;
        }])
        .value('providerTypes', {
            aap: {
                label: 'AAP',
                templateUrl: 'scripts/superdesk/items/views/aapConfig.html'
            },
            reuters: {
                label: 'Reuters',
                templateUrl: 'scripts/superdesk/items/views/reutersConfig.html'
            }
        })
        .config(function($routeProvider) {
            $routeProvider.
                when('/archive/', {
                    templateUrl: 'scripts/superdesk/items/views/archive.html',
                    controller: require('superdesk/items/controllers/list'),
                    resolve: {
                        items: ['locationParams', 'em', function(locationParams, em) {
                            var criteria = locationParams.reset({
                                where: {type: 'text'},
                                sort: ['firstcreated', 'desc'],
                                max_results: 25
                            });
                            return em.getRepository('items').matching(criteria);
                        }]
                    },
                    menu: {
                        label: gettext('Archive'),
                        priority: -2
                    }
                }).
                when('/archive/:id', {
                    templateUrl: 'scripts/superdesk/items/views/edit.html',
                    controller: require('superdesk/items/controllers/edit'),
                    resolve: {
                        item: ['$route', 'server', function($route, server) {
                            return server.readById('items', $route.current.params.id);
                        }]
                    }
                });
        })
        .config(function(settingsProvider) {
            settingsProvider.register('ingest-feed', {
                label: gettext('Ingest Feed'),
                templateUrl: 'scripts/superdesk/items/views/settings.html'
            });
        })
        .run(function($rootScope) {
            // todo(petr) - remove from root scope, directive maybe?
            $rootScope.mode = {
                zen: false
            };
        })
        .filter('characterCount', function() {
            return function(input) {
                return $(input).text().length;
            };
        })
        .filter('wordCount', function() {
            var nonchar = /[^\w]/g;
            var whitesp = /\s+/;
            return function(input) {
                var text = $(input).text();
                return text.replace(nonchar, ' ').split(whitesp).length;
            };
        });
});
