define([
    'require',
    'angular',
    'lodash',
    'd3',
    'moment',
    'moment-timezone'
], function(require, angular, _, d3, moment) {
    'use strict';

    angular.module('superdesk.dashboard.world-clock', ['superdesk.dashboard'])
        .factory('tzdata', ['$resource', function($resource) {
            var filename = require.toUrl('./timezones-all.json');
            return $resource(filename);
        }])
        .directive('sdWorldclock', [function() {
            return {
                templateUrl: require.toUrl('./worldClock.html'),
                replace: true,
                restrict: 'A',
                controller: 'WorldClockController'
            };
        }])
        .controller('WorldClockConfigController', ['$scope', '$resource', 'notify', 'tzdata',
        function ($scope, $resource, notify, tzdata) {
            tzdata.get(function(data) {
                $scope.availableZones = _.union(
                    _.keys(data.zones),
                    _.keys(data.links)
                );
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
        .controller('WorldClockController', ['$scope', '$interval', 'tzdata',
        function ($scope, $interval, tzdata) {

            var interval, INTERVAL_DELAY = 500;

            function updateUTC() {
                $scope.utc = moment();
                $scope.$digest();
            }

            tzdata.get(function(data) {
                moment.tz.add(data);
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
