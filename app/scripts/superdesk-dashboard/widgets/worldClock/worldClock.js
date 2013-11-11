define([
    'angular',
    'moment',
    'angular-resource'
], function(angular, moment) {
    'use strict';

    angular.module('superdesk.dashboard.widgets.worldclock', ['ngResource']).
        factory('worldclock', ['$resource', 'widgetsPath', function($resource, widgetsPath) {
            return $resource(widgetsPath + 'worldClock/clock.json');
        }]).
        directive('sdWorldclock', ['widgetsPath', function(widgetsPath) {
            return {
                templateUrl : widgetsPath + 'worldClock/worldClock.html',
                replace: true,
                restrict: 'A',
                controller : 'WorldClockController'
            };
        }]).
        directive('sdClock', ['widgetsPath', function(widgetsPath) {
            return {
                templateUrl: widgetsPath + 'worldClock/worldClockBox.html',
                scope: {wtime: '=wtime'},
                replace: true,
                transclude: true,
            };
        }]).
        controller('WorldClockController', function ($scope, $timeout, worldclock, widgetService, widgets) {
                var configuration = widgetService.loadConfiguration('worldClock');
                if (configuration === null) {
                    configuration = widgets.worldClock.defaultConfiguration;
                    widgetService.saveConfiguration('worldClock', configuration);
                }

                var cityList = {};
                worldclock.get(function(data){
                    cityList = data;

                    $scope.perPage = 3;
                    $scope.page = 1;
                    $scope.maxPage = Math.ceil(configuration.cities.length / $scope.perPage);

                    $scope.cities = [];

                    $scope.update = function() {
                        $scope.wclock = [];
                        _.forEach($scope.cities, function(city) {
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

                    $scope.$watch('page', function(page) {
                        var index = ($scope.page - 1) * $scope.perPage;
                        $scope.cities = configuration.cities.slice(index, index + $scope.perPage);
                        $scope.update();
                    });
                });
            });
});
