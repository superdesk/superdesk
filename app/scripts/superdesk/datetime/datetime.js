define([
    'angular',
    'moment',
    'require',
    './group-dates-directive',
    './reldate-directive',
    './reldate-directive-complex'
], function(angular, moment, require) {
    'use strict';

    function DateTimeDirective() {

        function renderDate(date, elem) {
            var momentDate = moment(date);
            elem.html(momentDate.fromNow());
            elem.attr('title', momentDate.format('LLLL'));
        }

        return {
            scope: {date: '='},
            link: function datetimeLink(scope, elem) {
                scope.$watch('date', function watchDate(date) {
                    if (date) {
                        renderDate(date, elem);
                    }
                });
            }
        };
    }

    return angular.module('superdesk.datetime', [])

        .directive('sdGroupDates', require('./group-dates-directive'))
        .directive('sdReldate', require('./reldate-directive'))
        .directive('sdReldateComplex', require('./reldate-directive-complex'))
        .directive('sdDatetime', DateTimeDirective)

        .filter('reldate', function reldateFactory() {
            return function reldate(date) {
                return moment(date).fromNow();
            };
        });
});
