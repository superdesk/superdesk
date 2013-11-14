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
        .controller('WorldClockConfigurationController', ['$scope', '$resource', 'widgetsPath', 'tzdata',
        function ($scope, $resource, widgetsPath, tzdata) {
            var rawTimezoneData = {};
            $scope.selected = {};
            $scope.availableZones = [];
            $scope.selectedCount = 0;
            $scope.search = '';

            tzdata.get(function(timezoneData) {
                rawTimezoneData = timezoneData;
                _.forEach(timezoneData.zones, function(zoneData, zoneName) {
                    $scope.availableZones.push(zoneName);
                    $scope.selected[zoneName] = false;
                });
                _.forEach(timezoneData.links, function(target, source) {
                    $scope.availableZones.push(source);
                    $scope.selected[source] = false;
                });
                $scope.availableZones.sort(function(a, b) {
                    if (a > b) {
                        return 1;
                    } else if (a < b) {
                        return -1;
                    } else {
                        return 0;
                    }
                });
                $scope.rawSelected = _.cloneDeep($scope.selected);
                _.forEach($scope.configuration.zones, function(item) {
                    if ($scope.selected[item] !== undefined) {
                        $scope.selected[item] = true;
                    }
                });
            });
            
            $scope.$watch('selected', function(selected) {
                if (!_.isEmpty(selected)) {
                    $scope.selectedCount = 0;
                    _.forEach(selected, function(value, key) {
                        if (value === true) {
                            $scope.selectedCount = $scope.selectedCount + 1;
                            $scope.configuration.zones.push(key);
                        } else {
                            $scope.configuration.zones = _.without($scope.configuration.zones, key);
                        }
                    });
                    $scope.configuration.zones = _.uniq($scope.configuration.zones);
                }
            }, true);

            $scope.clear = function() {
                $scope.selected = _.cloneDeep($scope.rawSelected);
            };
        }])
        .controller('WorldClockController', ['$scope', '$timeout', 'tzdata',
        function ($scope, $timeout, tzdata) {
            function updateUTC() {
                $scope.utc = moment();
                $timeout(updateUTC, 500);
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
                        r = Math.min(width, height) * 0.8 * 0.5;

                    var svg = d3.select(element[0])
                        .append('svg')
                            .attr('widgth', width)
                            .attr('height', height);

                    var clock = svg.append('g')
                        .attr('transform', 'translate(' + width / 2 + ',' + height / 2 + ')');

                    // background circle
                    clock.append('circle')
                        .attr('r', r)
                        .attr('class', 'clock outer')
                        .style('stroke', 'black')
                        .style('stroke-width', 1.3)
                        .style('fill', '#313134');

                    // inner dot
                    clock.append('circle')
                        .attr('r', 2)
                        .attr('class', 'clock inner')
                        .style('fill', '#fff');

                    // add markers
                    clock.selectAll('.mark')
                        .data(_.range(0, 60, 5))
                        .enter()
                        .append('path')
                        .attr('d', function(d) {
                            var angle = scales.m(d);
                            var arc = d3.svg.arc()
                                .innerRadius(r * 0.68)
                                .outerRadius(r * 0.9)
                                .startAngle(angle)
                                .endAngle(angle);
                            return arc();
                        })
                        .attr('class', 'mark')
                        .style('stroke-width', 2.1)
                        .style('stroke', '#828282');

                    // format data for given time
                    function getData(timeStr) {
                        var time = timeStr.split(':');
                        return [
                            {unit: 'h', val: parseInt(time[0], 10), width: 2.1, r: 0.5},
                            {unit: 'm', val: parseInt(time[1], 10), width: 1.3, r: 0.7},
                            {unit: 's', val: parseInt(time[2], 10), width: 0.8, r: 0.8}
                        ];
                    }

                    scope.$watch('utc', function(utc) {
                        var time = utc ? utc.tz(scope.tz).format('HH:mm:ss') : '00:00:00';
                        var data = getData(time);
                        clock.selectAll('.clockhand').remove();
                        clock.selectAll('.clockhand')
                            .data(data)
                            .enter()
                            .append('path')
                            .attr('d', function(d) {
                                var angle = scales[d.unit](d.val);
                                var arc = d3.svg.arc()
                                    .innerRadius(0)
                                    .outerRadius(r * d.r)
                                    .startAngle(angle)
                                    .endAngle(angle);
                                return arc();
                            })
                            .attr('class', 'clockhand')
                            .style('stroke-width', function(d) { return d.width; })
                            .style('stroke', function(d) { return d.unit === 's' ? '#f00' : '#fff'; })
                            .style('fill', 'none');
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
                    description: 'World clock widget'
                });
        }]);
});
