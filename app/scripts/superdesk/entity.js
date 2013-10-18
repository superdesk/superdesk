define(['angular', 'lodash', './server'], function(angular, _) {
    'use strict';

    angular.module('superdesk.entity', ['superdesk.server'])
        .service('locationParams', ['$location', '$route', function($location, $route) {
            return {
                defaults: {},

                reset: function(defaults) {
                    this.defaults = _.extend(defaults, {page: 1});
                    this.params = _.extend({}, this.defaults, $route.current.params);
                    return this.params;
                },

                get: function(key) {
                    return key in this.params ? this.params[key] : null;
                },

                set: function(key, val) {
                    var locVar = (key in this.defaults && angular.equals(this.defaults[key], val)) ? null : val;
                    $location.search(key, locVar);
                }
            };
        }])
        .service('em', function(server) {
            function Repository(entity) {
                this.matching = function(criteria) {
                    return server.list(entity, criteria);
                };
            }

            return {
                getRepository: function(entity) {
                    return new Repository(entity);
                }
            };
        });
});