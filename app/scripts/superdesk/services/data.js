define(['angular', 'lodash'], function(angular, _) {
    'use strict';

    return angular.module('superdesk.services.data', [])
        /**
         * Location State Adapter for Data Layer
         */
        .service('LocationStateAdapter', ['$location', function($location) {
            this.get = function(key) {
                return arguments.length ? $location.search()[key] : $location.search();
            };

            this.set = function(key, val) {
                return $location.search(key, val);
            };
        }])
        .factory('DataAdapter', ['$rootScope', 'em', 'LocationStateAdapter', function($rootScope, em, LocationStateAdapter) {
            /**
             * Data Provider for given resource
             */
            return function DataAdapter(resource, params) {
                var _this = this;
                var state = LocationStateAdapter; // @todo implement storage state adapter
                var cancelWatch = angular.noop;
                var defaultParams = {page: 1};

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
                 * @param {Object} query
                 */
                function slowQueryLog(query) {
                    query.time = Date.now() - query.start;
                    if (query.time > 500) {
                        console.info('Slow query', query);
                    }
                }

                /**
                 * Execute query
                 *
                 * @param {Object} criteria
                 */
                this.query = function(criteria) {
                    _this.loading = true;
                    var query = {resource: resource, criteria: criteria, start: Date.now()};
                    var promise = em.getRepository(resource).matching(criteria);
                    promise.then(function(data) {
                        _this.loading = false;
                        slowQueryLog(query);
                        angular.extend(_this, data);
                    });

                    return promise;
                };

                /**
                 * Get/set current page
                 *
                 * @param {integer} page
                 */
                this.page = function(page) {
                    switch (arguments.length) {
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
                    switch (arguments.length) {
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
                    switch (arguments.length) {
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
                    console.info('find', resource, id);
                    return em.find(resource, id);
                };

                /**
                 * Reset default params
                 */
                this.reset = function(params) {
                    cancelWatch();

                    defaultParams = angular.extend({
                        max_results: 25,
                        page: 1,
                        where: {},
                        sort: [],
                        filters: [],
                        ttl: 0
                    }, params);

                    // main loop - update when query criteria change
                    cancelWatch = $rootScope.$watchCollection(function () {
                        return getQueryCriteria();
                    }, function(criteria) {
                        _this.query(criteria);
                    });
                };

                /**
                 * Force reload with same params
                 */
                this.reload = function() {
                    _this.query(getQueryCriteria());
                };

                if (params) {
                    this.reset(params);
                }
            };
        }]);
});
