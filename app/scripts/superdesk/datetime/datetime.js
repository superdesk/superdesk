define([
    'angular',
    'moment',
    'require',
    './date-range-directive',
    './group-dates-directive',
    './reldate-directive'
], function(angular, moment, require) {
    'use strict';

    return angular.module('superdesk.datetime', [])

        .directive('sdDateRange', require('./date-range-directive'))
        .directive('sdGroupDates', require('./group-dates-directive'))
        .directive('sdReldate', require('./reldate-directive'))

        .filter('reldate', function() {
            return function(date) {
                return moment(date).fromNow();
            };
        });
});
