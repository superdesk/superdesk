define([
    'angular'
], function(angular) {
    'use strict';

    angular.module('superdesk.settings.entity', ['superdesk.entity'])
        .factory('providerRepository', ['em', function(em) {
            var repository = em.getRepository('ingest_providers');
            return repository;
        }]);
});