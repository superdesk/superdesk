define([
    'angular',
    'moment',
    'moment-timezone',
    'angular-resource'
], function(angular, moment) {
    'use strict';

    angular.module('superdesk.dashboard.widgets.worldclock', ['ngResource'])
        .service('timezoneDataService', ['$q', '$resource', 'widgetsPath', function($q, $resource, widgetsPath) {
            this.get = function(regions) {
                if (typeof regions === 'string') {
                    regions = [regions];
                }

                var delay = $q.defer();

                var promises = [];
                _.forEach(regions, function(region) {
                    var filename = widgetsPath + 'worldClock/timezones-' + region + '.json';
                    promises.push($resource(filename).get().$promise);
                });

                $q.all(promises).then(function(data) {
                    var timezoneData = {links: {}, rules: {}, zones: {}};
                    _.forEach(data, function(item) {
                        timezoneData.links = _.extend(timezoneData.links, item.links);
                        timezoneData.rules = _.extend(timezoneData.rules, item.rules);
                        timezoneData.zones = _.extend(timezoneData.zones, item.zones);
                    });
                    delay.resolve(timezoneData);
                });

                return delay.promise;
            };
        }])
        .directive('sdWorldclock', ['widgetsPath', function(widgetsPath) {
            return {
                templateUrl : widgetsPath + 'worldClock/worldClock.html',
                replace: true,
                restrict: 'A',
                controller : 'WorldClockController'
            };
        }])
        .controller('WorldClockConfigurationController', ['$scope', '$resource', 'widgetsPath', 'timezoneDataService',
        function ($scope, $resource, widgetsPath, timezoneDataService) {
            var rawTimezoneData = {};
            $scope.selected = {};
            $scope.availableZones = {};
            $scope.selectedCount = 0;
            $scope.search = '';

            timezoneDataService.get('all').then(function(timezoneData) {
                rawTimezoneData = timezoneData;
                moment.tz.add(timezoneData);
                _.forEach(timezoneData.zones, function(zoneData, zoneName) {
                    var parts = [
                        zoneName.slice(0, zoneName.indexOf('/')),
                        zoneName.slice(zoneName.indexOf('/') + 1)
                    ];
                    if ($scope.availableZones[parts[0]] === undefined) {
                        $scope.availableZones[parts[0]] = [];
                    }
                    $scope.availableZones[parts[0]].push(parts[1]);
                    $scope.selected[zoneName] = false;
                });
                _.forEach(timezoneData.links, function(target, source) {
                    var parts = source.split('/');
                    if ($scope.availableZones[parts[0]] === undefined) {
                        $scope.availableZones[parts[0]] = [];
                    }
                    $scope.availableZones[parts[0]].push(parts[1]);
                    $scope.selected[source] = false;
                });
                _.forEach($scope.availableZones, function(value, key) {
                    value.sort(function(a, b) {
                        if (a > b) {
                            return 1;
                        } else if (a < b) {
                            return -1;
                        } else {
                            return 0;
                        }
                    });
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
        .controller('WorldClockController', ['$scope', '$timeout', 'widgetService', 'widgets', 'timezoneDataService',
        function ($scope, $timeout, widgetService, widgets, timezoneDataService) {
            /*
            // for selective timezone data file loading
            var regions = [];
            _.forEach($scope.widget.configuration.zones, function(zone) {
                var parts = zone.split('/');
                regions.push(parts[0].toLowerCase());
            });
            regions = _.uniq(regions);
            timezoneDataService.get(regions).then(function(timezoneData) {
                moment.tz.add(timezoneData);
                $scope.update();
            });
            */
            
            // temporary, loading all timezone data files
            timezoneDataService.get('all').then(function(timezoneData) {
                moment.tz.add(timezoneData);
                $scope.update();
            });

            $scope.update = function() {
                $scope.wclock = [];
                _.forEach($scope.widget.configuration.zones, function(zone) {
                    var full = moment().tz(zone);
                    $scope.wclock.push({
                        'city' : zone,
                        'full' : full.format('HH:mm'),
                        'hrs'  : full.format('HH'),
                        'min'  : full.format('mm'),
                        'sec'  : full.format('ss')
                    });
                });
                $timeout($scope.update, 1000);
            };

        }]);
});
