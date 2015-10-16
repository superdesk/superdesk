define([
    'require',
    'angular',
    'lodash',
    'd3',
    'moment',
    'moment-timezone'
], function(require, angular, _, d3, moment) {
    'use strict';

    angular.module('superdesk.dashboard.world-clock', [
        'superdesk.dashboard', 'ngResource'
    ])
        /**
         * @memberof superdesk.dashboard.world-clock
         * @ngdoc service
         * @name tzdata
         * @description
         *   A service that automatically fetches the time zone data from the
         *   server upon instantiaton and stores it internally for future use,
         *   avoiding the need to fetch it again every time when needed.
         */
        .factory('tzdata', ['$resource', function ($resource) {
            var filename = require.toUrl('./timezones-all.json'),
                tzResource = $resource(filename);

            /**
             * Returns a sorted list of all time zone names. If time zone data
             * has not yet been fetched from the server, an empty list is
             * returned.
             * To determine whether or not the data has been fetched yet, the
             * $promise property should be examined.
             *
             * @method getTzNames
             * @return {Array} a list of time zone names
             */
            tzResource.prototype.getTzNames = function () {
                return _.union(
                    _.keys(this.zones),
                    _.keys(this.links)
                ).sort();
            };

            // return an array that will contain the fetched data when
            // it arrives from the server
            return tzResource.get();
        }])

        .directive('sdWorldclock', [function() {
            return {
                templateUrl: require.toUrl('./worldClock.html'),
                replace: true,
                restrict: 'A',
                controller: 'WorldClockController'
            };
        }])

        /**
         * @memberof superdesk.dashboard.world-clock
         * @ngdoc controller
         * @name WorldClockConfigController
         * @description
         *   Controller for the world clock widget configuration modal.
         */
        .controller('WorldClockConfigController', ['$scope', 'notify', 'tzdata',
        function ($scope, notify, tzdata) {

            $scope.availableZones = [];

            tzdata.$promise.then(function () {
                $scope.availableZones = tzdata.getTzNames();
            });

            $scope.notify = function(action, zone) {
                if (action === 'add') {
                    notify.success(gettext('World clock added:') + ' ' + zone, 3000);
                } else if (action === 'remove') {
                    notify.success(gettext('World clock removed:') + ' ' + zone, 3000);
                }
            };

            $scope.notIn = function(haystack) {
                return function(needle) {
                    return haystack.indexOf(needle) === -1;
                };
            };

            $scope.configuration.zones = $scope.configuration.zones || [];
        }])

        /**
         * @memberof superdesk.dashboard.world-clock
         * @ngdoc controller
         * @name WorldClockController
         * @description
         *   Controller for the sdWorldclock directive - the one that creates
         *   a dashboard widget for displaying the current time in different
         *   time zones around the world.
         */
        .controller('WorldClockController', ['$scope', '$interval', 'tzdata',
        function ($scope, $interval, tzdata) {

            var interval, INTERVAL_DELAY = 500;

            function updateUTC() {
                $scope.utc = moment();
                $scope.$digest();
            }

            // XXX: a hack-ish workaround to expose the object loaded via
            // RequireJS to the testing code which does not use the latter
            this._moment = moment;

            tzdata.$promise.then(function () {
                moment.tz.add(
                    _.pick(tzdata, ['zones', 'links'])
                );
            });

            interval = $interval(updateUTC, INTERVAL_DELAY, 0, false);
            $scope.$on('$destroy', function stopTimeout() {
                $interval.cancel(interval);
            });
        }])
        /**
         * sdClock analog clock
         */
        .directive('sdClock', function() {
            var pi = Math.PI,
                scales = {
                    s: d3.scale.linear().domain([0, 59 + 999 / 1000]).range([0, 2 * pi]),
                    m: d3.scale.linear().domain([0, 59 + 59 / 60]).range([0, 2 * pi]),
                    h: d3.scale.linear().domain([0, 11 + 59 / 60]).range([0, 2 * pi])
                };

            return {
                scope: {
                    'utc': '=',
                    'tz': '@'
                },
                link: function(scope, element, attrs) {
                    var width = 105,
                        height = 100,
                        r = Math.min(width, height) * 0.8 * 0.5,
                        dayBg = '#d8d8d8',
                        dayClockhands = '#313131',
                        dayNumbers = '#a0a0a0',
                        nightBg = '#313131',
                        nightClockhands = '#e0e0e0',
                        nightNumbers = '#848484';

                    var svg = d3.select(element[0])
                        .append('svg')
                            .attr('widgth', width)
                            .attr('height', height);

                    var clock = svg.append('g')
                        .attr('transform', 'translate(' + width / 2 + ',' + height / 2 + ')');

                    // background circle
                    clock.append('circle')
                        .attr('r', r)
                        .attr('class', 'clock-outer')
                        .style('stroke-width', 1.5);

                    // inner dot
                    clock.append('circle')
                        .attr('r', 1.5)
                        .attr('class', 'clock-inner');

                    // numbers
                    clock.selectAll('.number-lines')
                        .data(_.range(0, 59, 5))
                        .enter()
                        .append('path')
                            .attr('d', function(d) {
                                var angle = scales.m(d);
                                var arc = d3.svg.arc()
                                    .innerRadius(r * 0.7)
                                    .outerRadius(r * 0.9)
                                    .startAngle(angle)
                                    .endAngle(angle);
                                return arc();
                            })
                        .attr('class', 'number-lines')
                        .style('stroke-width', 1.5);

                    // format data for given time
                    function getData(timeStr) {
                        var time = timeStr.split(':');
                        return [
                            {unit: 'h', val: parseInt(time[0], 10) + (parseInt(time[1], 10) / 60), r: 0.5},
                            {unit: 'm', val: parseInt(time[1], 10), r: 0.8}
                        ];
                    }

                    scope.$watch('utc', function(utc) {
                        var time = utc ? utc.tz(scope.tz).format('HH:mm:ss') : '00:00:00';
                        var data = getData(time);
                        var isDay = data[0].val >= 8 && data[0].val < 20;

                        if (isDay) {
                            clock.selectAll('.clock-outer').style('fill', dayBg);
                            clock.selectAll('.clock-inner').style('fill', dayBg);
                            clock.selectAll('.number-lines').style('stroke', dayNumbers);
                        } else {
                            clock.selectAll('.clock-outer').style('fill', nightBg);
                            clock.selectAll('.clock-inner').style('fill', nightBg);
                            clock.selectAll('.number-lines').style('stroke', nightNumbers);
                        }

                        clock.selectAll('.clockhand').remove();
                        clock.selectAll('.clockhand')
                            .data(data)
                            .enter()
                            .append('path')
                            .attr('d', function(d) {
                                var angle = scales[d.unit](d.val);
                                var arc = d3.svg.arc()
                                    .innerRadius(r * 0)
                                    .outerRadius(r * d.r)
                                    .startAngle(angle)
                                    .endAngle(angle);
                                return arc();
                            })
                            .attr('class', 'clockhand')
                            .style('stroke-width', 2)
                            .style('stroke', isDay ? dayClockhands : nightClockhands);
                    });
                }
            };
        })
        .config(['widgetsProvider', function(widgetsProvider) {
            widgetsProvider.widget('world-clock', {
                label: gettext('World Clock'),
                multiple: true,
                icon: 'time',
                max_sizex: 2,
                max_sizey: 1,
                sizex: 1,
                sizey: 1,
                thumbnail: require.toUrl('./thumbnail.svg'),
                template: require.toUrl('./widget-worldclock.html'),
                configurationTemplate: require.toUrl('./configuration.html'),
                configuration: {zones: ['Europe/London', 'Asia/Tokyo', 'Europe/Moscow']},
                description: gettext('World clock widget')
            });
        }]);
});
