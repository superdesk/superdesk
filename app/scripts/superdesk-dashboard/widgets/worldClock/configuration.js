define([
    'angular',
    'moment',
    'moment-timezone'
], function(angular, moment){
    'use strict';

    return ['$scope', '$resource', 'widgetsPath', 'timezoneDataService',
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
    }];
});