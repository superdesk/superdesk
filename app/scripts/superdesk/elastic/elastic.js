define([
    'angular',
    './es'
], function(angular, ElasticSearchService) {
    'use strict';

    return angular.module('superdesk.elastic', [])
        .service('es', ElasticSearchService);
});
