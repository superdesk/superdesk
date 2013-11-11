define(['angular'], function(angular){
    'use strict';

    return ['$scope', '$resource', 'widgetsPath', 'worldclock',
    function ($scope, $resource, widgetsPath, worldclock) {
        worldclock.get(function(data) {
            $scope.cities = data;
        });

        $scope.check = function(city) {
            if (_.indexOf($scope.configuration.cities, city) === -1) {
                return false;
            } else {
                return true;
            }
        };

        $scope.add = function() {
            var newIndex = false;
            _.forEach(_.keys($scope.cities), function(city, index) {
                if (newIndex === false) {
                    if (_.indexOf($scope.configuration.cities, city) === -1) {
                        newIndex = index;
                    }
                }
            });
            if ($scope.cities[_.keys($scope.cities)[newIndex]].zone) {
                $scope.configuration.cities.push(_.keys($scope.cities)[newIndex]);
            }
        };

        $scope.remove = function(index) {
            $scope.configuration.cities = _.without($scope.configuration.cities, $scope.configuration.cities[index]);
        };

    }];
});