define([
    'jquery',
    'angular'
], function($, angular) {
    'use strict';

    angular.module('superdesk.dashboard.filters', []).
        filter('wcodeFilter', function() {
            return function(input, values) {
                return _.pick(input, _.difference(_.keys(input), _.keys(values)));
            };
        });
});