define([
    'jquery',
    'angular'
], function($, angular) {
    'use strict';

    angular.module('superdesk.filters', []).
        filter('any', function() {
            return function(data, key) {
                return _.any(data, key);
            };
        });
});