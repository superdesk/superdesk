define([
    'angular',
    'moment',
    'require',
    './group-dates-directive',
    './reldate-directive',
    './reldate-directive-complex',
    './absdate-directive'
], function(angular, moment, require) {
    'use strict';

    function DateTimeDirective() {
        return {
            scope: {date: '='},
            link: function datetimeLink(scope, elem) {
                scope.$watch('date', renderDate);

                /**
                 * Render relative date within given directive
                 *
                 * @param {string} date iso date
                 */
                function renderDate(date) {
                    var momentDate = moment(date);
                    elem.text(momentDate.fromNow());
                    elem.attr('title', momentDate.format('LLLL'));
                }
            }
        };
    }

    return angular.module('superdesk.datetime', [])

        .directive('sdGroupDates', require('./group-dates-directive'))
        .directive('sdReldate', require('./reldate-directive'))
        .directive('sdReldateComplex', require('./reldate-directive-complex'))
        .directive('sdAbsdate', require('./absdate-directive'))
        .directive('sdDatetime', DateTimeDirective)

        .filter('reldate', function reldateFactory() {
            return function reldate(date) {
                return moment(date).fromNow();
            };
        })

        .constant('moment', moment)

        .factory('weekdays', ['gettext', function(gettext) {
            return Object.freeze({
                MON: gettext('Monday'),
                TUE: gettext('Tuesday'),
                WED: gettext('Wednesday'),
                THU: gettext('Thursday'),
                FRI: gettext('Friday'),
                SAT: gettext('Saturday'),
                SUN: gettext('Sunday')
            });
        }])

        ;
});
