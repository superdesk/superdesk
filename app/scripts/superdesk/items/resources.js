define(['angular'], function(angular) {
    'use strict';

    function apiUrl() {
        var args = Array.prototype.slice.call(arguments);
        return config.api_url + args.join('/') + '/';
    }

    angular.module('superdesk.items.resources', ['superdesk.auth.services']).
        factory('ItemsLoader', function($q, $http) {
            return function() {
                var delay = $q.defer();
                $http.get(apiUrl('items'), {params: {sort: '[("firstCreated", -1)]'}}).
                    then(function(response) {
                        delay.resolve(response.data._items);
                    });
                return delay.promise;
            };
        }).
        factory('ItemLoader', function($q, $http, $route) {
            return function(guid) {
                if (typeof guid === 'undefined' && 'guid' in $route.current.params) {
                    guid = $route.current.params.guid;
                }

                var delay = $q.defer();
                $http.get(apiUrl('items', guid)).
                    then(function(response) {
                        delay.resolve(response.data);
                    });
                return delay.promise;
            };
        });
});