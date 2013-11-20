define([
    'angular',
    'moment',
    'd3',
    'moment-timezone',
    'angular-resource',
    '../../services'
], function(angular, moment, d3) {
    'use strict';

    angular.module('superdesk.widgets.worldClock', ['ngResource', 'superdesk.dashboard.services'])
        .factory('tzdata', ['$resource', 'widgetsPath', function($resource, widgetsPath) {
            var filename = widgetsPath + 'worldClock/timezones-all.json';
            return $resource(filename);
        }])
        .directive('sdWorldclock', ['widgetsPath', function(widgetsPath) {
            return {
                templateUrl : widgetsPath + 'worldClock/worldClock.html',
                replace: true,
                restrict: 'A',
                controller : 'WorldClockController'
            };
        }])
        .controller('WorldClockConfigController', ['$scope', '$resource', 'tzdata',
        function ($scope, $resource, tzdata) {
            tzdata.get(function(data) {
                $scope.availableZones = _.union(
                    _.keys(data.zones),
                    _.keys(data.links)
                );
            });

            $scope.notIn = function(haystack) {
                return function(needle) {
                    return haystack.indexOf(needle) === -1;
                };
            };
        }])
        .controller('WorldClockController', ['$scope', '$timeout', 'tzdata',
        function ($scope, $timeout, tzdata) {
            function updateUTC() {
                $scope.utc = moment();
                $timeout(updateUTC, 1000);
            }

            tzdata.get(function(data) {
                moment.tz.add(data);
                updateUTC();
            });
        }])
        /**
         * sdClock analog clock
         */
        .directive('sdClock', function() {
            var pi = Math.PI,
                scales = {
                    s: d3.scale.linear().domain([0, 59 + 999/1000]).range([0, 2 * pi]),
                    m: d3.scale.linear().domain([0, 59 + 59/60]).range([0, 2 * pi]),
                    h: d3.scale.linear().domain([0, 11 + 59/60]).range([0, 2 * pi])
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
                        white = '#fff',
                        black = '#333';

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
                        .style('stroke-width', 1.5)
                        .style('stroke', black);

                    // inner dot
                    clock.append('circle')
                        .attr('r', 1.5)
                        .attr('class', 'clock-inner');

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
                            clock.selectAll('.clock-outer').style('fill', white);
                            clock.selectAll('.clock-inner').style('fill', black);
                        } else {
                            clock.selectAll('.clock-outer').style('fill', black);
                            clock.selectAll('.clock-inner').style('fill', white);
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
                            .style('stroke-width', 1.5)
                            .style('stroke', isDay ? black : white);
                    });
                }
            };
        })
        .config(['widgetsProvider', function(widgetsProvider) {
            widgetsProvider
                .widget('worldClock', {
                    name: 'World Clock',
                    class: 'world-clock',
                    icon: 'time',
                    max_sizex: 2,
                    max_sizey: 1,
                    sizex: 1,
                    sizey: 1,
                    thumbnail: 'images/sample/widgets/worldclock.png',
                    template: 'scripts/superdesk-dashboard/widgets/worldClock/widget-worldclock.html',
                    configurationTemplate: 'scripts/superdesk-dashboard/widgets/worldClock/configuration.html',
                    configuration: {zones: ['Europe/London', 'Asia/Tokyo', 'Europe/Moscow']},
                    description: 'World clock widget',
                    multiple: true
                });
        }]);
});
