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
                restrict: 'E'
            };
        }]).
        controller('WorldClockController', function ($scope, worldclock, $timeout) {
                var limit = 3;
                var skip = 0;

                $scope.showleft = false;
                $scope.showright = true;

                var city = [];
                worldclock.get(function(data){
                    city = data.city;
                    $scope.WCtick();
                });

                $scope.wclock = [];

                $scope.skipNext = function () {
                    if ($scope.showright) {
                        skip += limit;
                        $scope.showArrows();
                        $scope.WCtick();
                    }
                };

                $scope.showArrows = function() {
                    if ((skip+limit) >= city.length) {
                        $scope.showright = false;
                    } else {
                        $scope.showright = true;
                    }

                    if (skip <= 0) {
                        skip = 0;
                        $scope.showleft = false;
                    } else {
                        $scope.showleft = true;
                    }
                };

                $scope.skipPrev = function () {
                    if ($scope.showleft) {
                        skip -= limit;
                        $scope.showArrows();
                        $scope.WCtick();
                    }
                };

                $scope.WCtick = function() {
                    $scope.wclock = [];
                    for (var i = skip; i < (skip + limit); i++) {
                        if (city[i] !== undefined ) {
                            var full = moment().zone(-city[i].zone-city[i].daylight);
                            $scope.wclock[i-skip] = {
                                'city' : city[i].name,
                                'full' : full.format('HH:mm'),
                                'hrs'  : full.format('HH'),
                                'min'  : full.format('mm'),
                                'sec'  : full.format('ss')
                            };
                        }
                    }
                    $timeout($scope.WCtick, 1000);
                };
            });
});
