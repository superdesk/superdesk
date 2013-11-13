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
        .controller('WorldClockController', ['$scope', '$timeout', 'widgetService', 'widgets', 'timezoneDataService',
        function ($scope, $timeout, widgetService, widgets, timezoneDataService) {
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
