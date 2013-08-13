define(['angular'], function(angular) {
    'use strict';

    angular.module('superdesk.items.resources', ['superdesk.auth.services']).
        factory('ItemsLoader', function($q, $http) {
            return function() {
                var delay = $q.defer();
                $http.get(config.api_url + '/items/', {params: {sort: '[("firstCreated", -1)]'}}).
                    then(function(response) {
                        delay.resolve(response.data._items);
                    });
                return delay.promise;
            };
        });
});