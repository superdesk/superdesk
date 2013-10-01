define([
    'angular',
    'moment'
], function(angular) {
    'use strict';

    angular.module('superdesk.dashboard.resources', []).
        factory('worldclock', function($timeout) {
            
            var time = [];
            var city = [
                {'name' : 'London',   'zone' : '0',  'daylight' : '1' },
                {'name' : 'New York', 'zone' : '-5', 'daylight' : '1' },
                {'name' : 'Sydney',   'zone' : '10', 'daylight' : '0' }
            ];

            (function tick() {
                angular.forEach(city, function(cityinfo, key) {
                    var full = moment().zone(-cityinfo['zone']-cityinfo['daylight']);
                    time[key] = { 
                        'city' : cityinfo['name'],
                        'full' : full.format("HH:mm"),
                        'hrs'  : full.format("HH"),
                        'min'  : full.format("mm"),
                        'sec'  : full.format("ss")
                    }
                });
                $timeout(tick, 1000);
            })();

            return time;
        })
        
});