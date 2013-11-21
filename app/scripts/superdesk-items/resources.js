define(['angular'], function(angular) {
    'use strict';

    angular.module('superdesk.items.resources', ['superdesk.server'])
        .service('ItemService', function(server) {
            return {
                update: function(item) {
                    server.update(item);
                }
            };
        })
        .factory('colorSchemes', function($resource) {
            return $resource('scripts/superdesk-items/static-resources/color-schemes.json');
        })
        .factory('providerRepository', ['em', function(em) {
            var repository = em.getRepository('ingest_providers');

            /**
             * Find all registered providers
             */
            repository.findAll = function() {
                return repository.matching({sort: ['created', 'desc'], max_results: 50});
            };

            return repository;
        }]);
});
