define(['angular', 'lodash'], function(angular, _) {
    'use strict';

    angular.module('superdesk.services')
        .factory('DataAdapter', ['$rootScope', '$location', 'em', function($rootScope, $location, em) {
            /**
             * $location state adapter
             */
            function LocationState(loc) {

                this.get = function(key) {
                    return arguments.length ? loc.search()[key] : loc.search();
                };

                this.set = function(key, val) {
                    return loc.search(key, val);
                };
            }

            // @todo implement storage state provider
            var stateProviders = {
                location: new LocationState($location)
            };

            /**
             * Data Provider for given resource
             */
            return function DataAdapter(resource, params) {
                var _this = this;
                var state = stateProviders.location;
                var defaultParams = angular.extend({max_results: 25, page: 1, where: {}, sort: [], filters: []}, params);

                /**
                 * Get query criteria - extend default params with current search
                 */
                function getQueryCriteria() {
                    var criteria = angular.extend({}, defaultParams, state.get());
                    angular.extend(criteria.where, _.pick(state.get(), defaultParams.filters));

                    if (criteria.hasOwnProperty('_id')) {
                        // prevent reload on preview
                        delete criteria._id;
                    }

                    return criteria;
                }

                /**
                 * Log slow query into console
                 *
                 * @param {integer} start
                 */
                function slowQueryLog(start) {
                    var took = Date.now() - start;
                    if (took > 500) {
                        console.log('Slow query: /' + resource + ' ' + took + 'ms');
                    }
                }

                /**
                 * Execute query
                 *
                 * @param {Object} criteria
                 */
                function query(criteria) {
                    var start = Date.now();
                    _this._items = null;
                    return em.getRepository(resource).matching(criteria).then(function(data) {
                        slowQueryLog(start);
                        angular.extend(_this, data);
                    });
                }

                /**
                 * Get/set current page
                 *
                 * @param {integer} page
                 */
                this.page = function(page) {
                    switch(arguments.length) {
                        case 0:
                            return state.get('page') || defaultParams.page;

                        case 1:
                            if (this._items) {
                                state.set('page', page !== defaultParams.page ? page : null);
                            }
                    }
                };

                /**
                 * Get/set current search query
                 *
                 * @param {string} q
                 * @param {string} df
                 */
                this.search = function(q, df) {
                    switch(arguments.length) {
                        case 0:
                            return state.get('q');

                        case 1:
                            if (this._items) {
                                state.set('q', q);
                                state.set('df', df);
                                state.set('page', null);
                            }
                    }

                    return this;
                };

                /**
                 * Get/set filter
                 *
                 * @param {string} key
                 * @param {string} val
                 */
                this.where = function(key, val) {
                    switch(arguments.length) {
                        case 1:
                            return state.get(key) || null;

                        case 2:
                            state.set(key, val || null);
                            state.set('page', null);
                    }

                    return this;
                };

                /**
                 * Get single item by id
                 */
                this.find = function(id) {
                    return em.find(resource, id);
                };

                $rootScope.$watch(function watchQueryCriteria() {
                    return getQueryCriteria();
                }, function(criteria) {
                    query(criteria);
                }, true);
            };
        }]);
});
