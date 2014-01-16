define(['angular', 'lodash'], function(angular, _) {
    'use strict';

    angular.module('superdesk.services')
    .factory('DataAdapter', ['$rootScope', '$location', '$route', 'em', function($rootScope, $location, $route, em) {
        /**
         * Data Provider for given resource
         */
        return function DataAdapter(resource, params) {
            var _this = this;
            var defaultParams = angular.extend({max_results: 25, page: 1, where: {}, sort: [], filters: []}, params);

            /**
             * Get query criteria - extend default params with current route params
             */
            function getQueryCriteria() {
                var criteria = angular.extend({}, defaultParams, $route.current.params);
                angular.extend(criteria.where, _.pick($route.current.params, defaultParams.filters));

                if (criteria.hasOwnProperty('_id')) {
                    // prevent reload on preview
                    delete criteria['_id'];
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
                    return $route.current.params.page || defaultParams.page;
                    break;

                    case 1:
                    if (this._items) {
                        $location.search('page', page !== defaultParams.page ? page : null);
                    }
                    break;
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
                    return $route.current.params.q;
                    break;

                    case 1:
                    if (this._items) {
                        $location.search('q', q);
                        $location.search('df', df);
                        $location.search('page', null);
                    }
                    break;
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
                    case 2:
                    $location.search(key, val || null);
                    $location.search('page', null);
                    break;

                    case 1:
                    return $route.current.params[key] || null;
                    break;
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
