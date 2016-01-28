(function() {
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

    return angular.module('superdesk.datetime', [
        'superdesk.datetime.absdate',
        'superdesk.datetime.groupdates',
        'superdesk.datetime.reldatecomplex',
        'superdesk.datetime.reldate'
    ])
        .directive('sdDatetime', DateTimeDirective)

        .filter('reldate', function reldateFactory() {
            return function reldate(date) {
                return moment(date).fromNow();
            };
        })

        // format datetime obj to time string
        .filter('time', function timeFilterFactory() {
            return function timeFilter(date) {
                return moment(date).format('h:mm');
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
        }]);
})();
