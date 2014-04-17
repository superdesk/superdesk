define(['angular', 'moment'], function(angular, moment) {
    'use strict';

    return angular.module('superdesk.datetime', [])
        .filter('reldate', function() {
            return function(date) {
                return moment(date).fromNow();
            };
        });
});
