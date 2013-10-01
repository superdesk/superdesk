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
                UserResource.query(
                    angular.extend({}, defaultParams, params, $route.current.params),
                    function(response) {
                        delay.resolve(response);
                    },
                    function(response) {
                        delay.reject(response);
                    });
                return delay.promise;
            };
        }).
        factory('UserLoader', function($q, $route, UserResource) {
            return function(id) {
                if (typeof id === 'undefined' && 'guid' in $route.current.params) {
                    id = $route.current.params.id;
                }

                var delay = $q.defer();
                UserResource.get({id: id},
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
                    UserResource.update(user, function(response) {
                        angular.extend(user, response);
                    });
                }
            };
        })
});