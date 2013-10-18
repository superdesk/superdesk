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
                this.matching = function(criteria) {
                    return server.list(entity, criteria);
                };
            }

            /**
             * Entity Manager
             */
            function EntityManager() {

                /**
                 * Get repository for given entity
                 *
                 * @param {string} entity
                 * @return {Repository)
                 */
                this.getRepository = function(entity) {
                    return new Repository(entity);
                };
            }

            return new EntityManager();
        });
});