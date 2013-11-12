define([
    'angular',
    'moment',
    'moment-timezone'
], function(angular, moment){
    'use strict';

    return ['$scope', '$resource', 'widgetsPath', 'widgetService',
    function ($scope, $resource, widgetsPath, widgetService) {
        var rawTimezoneData = {};
        $scope.selected = {};
        $scope.availableZones = {};
        $scope.selectedCount = 0;

        widgetService.getTimezoneData('all').then(function(timezoneData) {
            rawTimezoneData = timezoneData;
            moment.tz.add(timezoneData);
            _.forEach(timezoneData.zones, function(zoneData, zoneName) {
                if (_.indexOf(zoneName, '/') !== -1) {
                    var parts = [
                        zoneName.slice(0, zoneName.indexOf('/')),
                        zoneName.slice(zoneName.indexOf('/') + 1)
                    ];
                    if ($scope.availableZones[parts[0]] === undefined) {
                        $scope.availableZones[parts[0]] = [];
                    }
                    $scope.availableZones[parts[0]].push(parts[1]);
                    $scope.selected[zoneName] = false;
                } else {
                    if ($scope.availableZones.Generic === undefined) {
                        $scope.availableZones.Generic = [];
                    }
                    $scope.availableZones.Generic.push(zoneName);
                }
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