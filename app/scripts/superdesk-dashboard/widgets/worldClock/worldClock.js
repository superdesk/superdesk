define([
    'angular',
    'moment',
    'moment-timezone',
    'angular-resource'
], function(angular, moment) {
    'use strict';

    angular.module('superdesk.dashboard.widgets.worldclock', ['ngResource'])
        .directive('sdWorldclock', ['widgetsPath', function(widgetsPath) {
            return {
                templateUrl : widgetsPath + 'worldClock/worldClock.html',
                replace: true,
                restrict: 'A',
                controller : 'WorldClockController'
            };
        }])
        .controller('WorldClockController', ['$scope', '$timeout', 'widgetService', 'widgets',
        function ($scope, $timeout, widgetService, widgets) {
            //console.log($scope.widget.configuration);

            /*
            var cityList = {};
            worldclock.get(function(data){
                cityList = data;
                $scope.update();
            });

            $scope.update = function() {
                $scope.wclock = [];
                _.forEach($scope.widget.configuration.cities, function(city) {
                    var full = moment().zone(-cityList[city].zone-cityList[city].daylight);
                    $scope.wclock.push({
                        'city' : city,
                        'full' : full.format('HH:mm'),
                        'hrs'  : full.format('HH'),
                        'min'  : full.format('mm'),
                        'sec'  : full.format('ss')
                    });
                });

                $timeout($scope.update, 1000);
            };
            */
        }]);
});
