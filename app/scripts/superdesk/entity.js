define(['angular', 'lodash', './server'], function(angular, _) {
    'use strict';

    /**
     * Entity module
     */
    angular.module('superdesk.entity', ['superdesk.server'])

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
                    return key in this.params ? this.params[key] : null;
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
                    var parts = [];
                    _.forEach(this.params, function(val, key) {
                        if (!angular.equals(this.defaults[key], val)) {
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
                }
            };
        }])

        /**
         * Entity manager service
         */
        .service('em', function(server) {
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
                    return server.list(entity, criteria);
                };
            }

            /**
             * Entity Manager
             */
            function EntityManager() {

                this._repositories = {};

                /**
                 * Get repository for given entity
                 *
                 * @param {string} entity
                 * @return {Repository)
                 */
                this.getRepository = function(entity) {
                    if (!(entity in this._repositories)) {
                        this._repositories[entity] = new Repository(entity);
                    }

                    return this._repositories[entity];
                };

                /**
                 * Remove given item
                 *
                 * @param {Object} item
                 * @return {Object}
                 */
                this.remove = function(item) {
                    return this.server.delete(item);
                };

                /**
                 * Update given item
                 *
                 * @param {Object} item
                 * @return {Object}
                 */
                this.update = function(item) {
                    return this.server.update(item);
                };

                /**
                 * Persist given item
                 *
                 * @param {Object} item
                 * @return {Object}
                 */
                this.persist = function(item, entity) {
                    return this.server.create(entity, item);
                };
            }

            return new EntityManager();
        });
});