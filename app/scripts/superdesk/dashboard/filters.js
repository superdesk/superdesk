define([
    'jquery',
    'angular'
], function($, angular) {
    'use strict';

    angular.module('superdesk.dashboard.filters', []).
        filter('wcodeFilter', function() {
            return function(input, values) {
                return _.filter(input, function(item) {
                    if (_.indexOf(
                        _.difference(
                            _.pluck(input, 'wcode'),
                            _.pluck(values, 'wcode')
                        ), item.wcode) !== -1) {
                        return true;
                    }
                });
            };
        });
});