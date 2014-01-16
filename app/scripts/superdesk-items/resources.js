define(['angular'], function(angular) {
    'use strict';

    angular.module('superdesk.items.resources', [])
        .factory('colorSchemes', ['$resource', function($resource) {
            return $resource('scripts/superdesk-items/static-resources/color-schemes.json');
        }])
        .factory('providerRepository', ['em', function(em) {
            var repository = em.getRepository('ingest_providers');

            /**
             * Find all registered providers
             */
            repository.findAll = function() {
                return repository.matching({sort: ['created', 'desc'], max_results: 50});
            };

            return repository;
        }])
        .factory('panes', function () {

            var panes = [{
                name: 'Sources',
                icon:'sources',
                template: 'scripts/superdesk-items/views/panes/pane-blank.html',
                position: 'left',
                active: false,
                selected: true
            },
            {
                name: 'Archive',
                icon:'archive',
                template: 'scripts/superdesk-items/views/panes/pane-blank.html',
                position: 'left',
                active: false,
                selected: true
            },
            {
                name: 'Desks',
                icon:'desks',
                template: 'scripts/superdesk-items/views/panes/pane-blank.html',
                position: 'left',
                active: false,
                selected: true
            },
            {
                name: 'Info',
                icon:'info',
                template: 'scripts/superdesk-items/views/panes/pane-blank.html',
                position: 'right',
                active: false,
                selected: true
            },
            {
                name: 'Chat',
                icon:'chat',
                template: 'scripts/superdesk-items/views/panes/pane-blank.html',
                position: 'right',
                active: false,
                selected: true
            }, 
            {
                name: 'Editorial comments',
                icon:'editorial',
                template: 'scripts/superdesk-items/views/panes/pane-blank.html',
                position: 'right',
                active: false,
                selected: true
            }, 
            {
                name: 'Media',
                icon:'media',
                template: 'scripts/superdesk-items/views/panes/pane-blank.html',
                position: 'right',
                active: false,
                selected: true
            }, 
            {
                name: 'Switches',
                icon:'switches',
                template: 'scripts/superdesk-items/views/panes/pane-blank.html',
                position: 'right',
                active: false,
                selected: true
            }, 
            {
                name: 'Geolocation',
                icon:'geolocation',
                template: 'scripts/superdesk-items/views/panes/pane-blank.html',
                position: 'right',
                active: false,
                selected: true
            }, 
            {
                name: 'Comments',
                icon:'comments',
                template: 'scripts/superdesk-items/views/panes/pane-blank.html',
                position: 'right',
                active: false,
                selected: true
            }, 
            {
                name: 'Follow Up',
                icon:'followup',
                template: 'scripts/superdesk-items/views/panes/pane-blank.html',
                position: 'right',
                active: false,
                selected: true
            }];

            return {
                query: function () {
                    return panes;
                },
                active: function (Pane) {
                    Pane.active = !Pane.active;
                }
            };
        });
});
