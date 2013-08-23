define([
    'angular',
    'superdesk/api'
], function(angular) {
    'use strict';

    angular.module('superdesk.items.resources', ['superdesk.api', 'superdesk.auth.services']).
        factory('ItemResource', function(resource) {
            return resource('/items', {guid: '@_id'}, {
                query: {method: 'GET', isArray: false},
                get: {method: 'GET', url: '/items/:guid'}
            });
        }).
        factory('ItemListLoader', function($q, ItemResource) {
            return function(params) {
                var delay = $q.defer();
                ItemResource.query(params,
                    function(response) {
                        var items = response.items;
                        items.has_next = response.has_next;
                        items.has_prev = response.has_prev;
                        delay.resolve(items);
                    },
                    function(response) {
                        delay.reject(response);
                    });
                return delay.promise;
            };
        }).
        factory('ItemLoader', function($q, $route, ItemResource) {
            return function(guid) {
                if (typeof guid === 'undefined' && 'guid' in $route.current.params) {
                    guid = $route.current.params.guid;
                }

                var delay = $q.defer();
                ItemResource.get({guid: guid},
                    function(response) {
                        delay.resolve(response);
                    },
                    function(response) {
                        delay.reject(response);
                    });
                return delay.promise;
            };
        }).
        service('ItemService', function($http) {
            return {
                update: function(item) {
                    return $http({
                        method: 'PATCH',
                        url: 'http://' + item._links.self.href,
                        data: item,
                        headers: {'If-Match': item.etag}
                    });
                }
            };
        })
});