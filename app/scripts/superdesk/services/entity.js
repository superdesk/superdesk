define([
    'angular',
    'lodash'
], function(angular, _) {
    'use strict';

    return angular.module('superdesk.services.entity', [])
        /**
         * Location Params service holds default params for given page
         * and combines those with current params.
         */
        .service('locationParams', ['$location', '$route', function($location, $route) {
            return {
                defaults: {},

                /**
                 * Set default params
                 *
                 * @param {Object} defaults
                 * @return {Object} defaults + current
                 */
                reset: function(defaults) {
                    this.defaults = _.extend(defaults, {page: 1});
                    this.params = _.extend({}, this.defaults, $route.current.params);
                    return this.params;
                },

                /**
                 * Get parameter
                 *
                 * @param {string} key
                 * @return {*}
                 */
                get: function(key) {
                    return this.params && this.params[key] ? this.params[key] : null;
                },

                /**
                 * Set location parameter and hits the $location.search
                 *
                 * if parameter value is same as default one it will remove it from $location
                 *
                 * @param {string} key
                 * @param {mixed} val
                 * @return {locationParams}
                 */
                set: function(key, val) {
                    var locVar = (key in this.defaults && angular.equals(this.defaults[key], val)) ? null : val;
                    $location.search(key, locVar);
                    return this;
                },

                /**
                 * Returns query string compiled from current params
                 *
                 * if parameter value is same as default one it will remove it from query
                 *
                 * @return {string}
                 */
                getQuery: function() {
                    return this.makeQuery(this.params, this.defaults);
                },

                /**
                 * Returns query string compiled from given params
                 *
                 * if parameter value is same as default one it will remove it from query
                 *
                 * @return {string}
                 */
                makeQuery: function(params, defaults) {
                    defaults = defaults || {};

                    var parts = [];
                    _.forEach(params, function(val, key) {
                        if (!angular.equals(defaults[key], val)) {
                            if (_.isArray(val) === false) {
                                val = [val];
                            }
                            _.forEach(val, function(item) {
                                parts.push(encodeURIComponent(key) + '=' + encodeURIComponent(item));
                            });
                        }
                    }, this);
                    var query = (parts.length === 0) ? '' : '?' + parts.join('&');
                    return query;
                },

                /**
                 * Updates url with given path, keeping parameters
                 *
                 * if parameter value is same as default one it will remove it from query
                 *
                 * @param {string} path
                 */
                path: function(path) {
                    $location.path(path);
                },

                /**
                 * Activates controller based on current url. Does not refresh the page.
                 *
                 *
                 */
                reload: function() {
                    $route.reload();
                },

                /**
                 * Replace history
                 */
                replace: function() {
                    $location.replace();
                }
            };
        }])

        /**
         * Entity manager service
         */
        .service('em', ['server', function(server) {
            /**
             * Entity repository
             */
            function Repository(entity) {

                /**
                 * Find entity by given id
                 *
                 * @param {string} id
                 * @return {Object}
                 */
                this.find = function(id) {
                    return server.readById(entity, id);
                };

                /**
                 * Find entities matching given criteria
                 *
                 * @param {Object} criteria
                 * @return {Object}
                 */
                this.matching = function(criteria) {
                    if (!criteria) {
                        criteria = {};
                    }

                    return server.list(entity, criteria);
                };

                /**
                 * Find all entities
                 *
                 * @return {Object}
                 */
                this.all = function() {
                    return this.matching();
                };
            }

            var repos = {};

            /**
             * Get repository for given entity
             *
             * @param {string} entity
             * @return {Repository)
             */
            this.getRepository = function(entity) {
                if (!(entity in repos)) {
                    repos[entity] = new Repository(entity);
                }

                return repos[entity];
            };

            /**
             * Shortcut for getRepository
             */
            this.repository = this.getRepository;

            /**
             * Remove given item
             *
             * @param {Object} item
             * @return {Object}
             */
            this['delete'] = function(item) {
                return server['delete'](item);
            };

            /**
             * Update given item
             *
             * @param {Object} item
             * @param {Object} updates
             * @return {Object}
             */
            this.update = function(item, updates) {
                return server.update(item, updates);
            };

            /**
             * Persist given item
             *
             * @param {string} resource
             * @param {Object} item
             * @return {Object}
             */
            this.create = function(resource, item) {
                return server.create(resource, item);
            };

            /**
             * Remove given item from repository
             *
             * @param {Object} item
             * @return {Object}
             */
            this.remove = function(item) {
                return this['delete'](item);
            };

            /**
             * Save item
             *
             * @param {string} resource
             * @param {Object} item
             * @return {Object}
             */
            this.save = function(resource, item) {
                if ('_etag' in item) {
                    return this.update(item);
                } else {
                    return this.create(resource, item);
                }
            };

            /**
             * Shortcut for em.repository(resource).find(id)
             *
             * @param {string} resource
             * @param {string} id
             * @return {Object}
             */
            this.find = function(resource, id) {
                return this.repository(resource).find(id);
            };
        }]);
});
