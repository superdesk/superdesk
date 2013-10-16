define([
    'angular',
    'superdesk/api'
], function(angular) {
    'use strict';

    angular.module('superdesk.items.resources', ['superdesk.api', 'superdesk.auth.services']).
        factory('ItemResource', function(resource) {
            return resource('/items/:guid', {guid: '@guid'}, {
                query: {method: 'GET', isArray: false},
                get: {method: 'GET'},
                update: {method: 'PUT'}
            });
        }).
        factory('itemListLoader', function($q, $route, ItemResource) {
            var defaultParams = {
                sort: '[("firstCreated", -1)]'
            };

            return function(params) {
                var delay = $q.defer();
                ItemResource.query(
                    angular.extend({where: params}, defaultParams, $route.current.params),
                    function(response) {
                        var items = response._items;
                        items.links = response._links;
                        delay.resolve(items);
                    },
                    function(response) {
                        delay.reject(response);
                    });
                return delay.promise;
            };
        }).
        factory('itemLoader', function($q, $route, ItemResource) {
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
        service('ItemService', function(ItemResource) {
            return {
                update: function(item) {
                    ItemResource.update(item, function(response) {
                        angular.extend(item, response);
                    });
                }
            };
        });
});