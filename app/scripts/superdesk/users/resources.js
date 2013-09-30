define([
    'angular',
    'superdesk/api'
], function(angular) {
    'use strict';

    angular.module('superdesk.users.resources', ['superdesk.api', 'superdesk.auth.services']).
        factory('UserResource', function(resource) {
            return resource('/users/:id', {id: '@id'}, {
                query: {method: 'GET', isArray: false},
                get: {method: 'GET'},
                update: {method: 'PUT'}
            });
        }).
        factory('UserListLoader', function($q, $route, UserResource) {
            var defaultParams = {
                sort: '[("firstCreated", -1)]',
                skip: 0,
                limit: 25
            };

            return function(params) {
                var delay = $q.defer();
                ItemResource.query(
                    angular.extend({}, defaultParams, params, $route.current.params),
                    function(response) {
                        var items = response.items;
                        items.has_next = response.has_next;
                        items.has_prev = response.has_prev;
                        items.total_length = 'total' in response ? response.total : null;
                        delay.resolve(items);
                    },
                    function(response) {
                        delay.reject(response);
                    });
                return delay.promise;
            };
        }).
        factory('UserLoader', function($q, $route, UserResource) {
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
        service('UserService', function(UserResource) {
            return {
                update: function(item) {
                    UserResource.update(item, function(response) {
                        angular.extend(item, response);
                    });
                }
            };
        })
});