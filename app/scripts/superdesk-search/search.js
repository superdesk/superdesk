(function() {
    'use strict';

    SearchService.$inject = ['$location', 'gettext'];
    function SearchService($location, gettext) {
        this.sortOptions = [
            {field: 'versioncreated', label: gettext('Updated')},
            {field: 'firstcreated', label: gettext('Created')},
            {field: 'urgency', label: gettext('News Value')},
            {field: 'priority', label: gettext('Priority')},
            {field: 'headline', label: gettext('Headline'), defaultDir: 'asc'}
        ];

        this.sort = function sort(field) {
            var option = _.find(this.sortOptions, {field: field});
            setSortSearch(option.field, option.defaultDir || 'desc');
        };

        this.getSort = function getSort() {
            var sort = ($location.search().sort || 'versioncreated:desc').split(':');
            return angular.extend(_.find(this.sortOptions, {field: sort[0]}), {dir: sort[1]});
        };

        this.toggleSortDir = function toggleSortDir() {
            var sort = this.getSort();
            var dir = sort.dir === 'asc' ? 'desc' : 'asc';
            setSortSearch(sort.field, dir);
        };

        function setSortSearch(field, dir) {
            $location.search('sort', field + ':' + dir);
            $location.search('page', null);
        }
    }

    ContentQueryBuilder.$inject = ['$location', 'search'];
    function ContentQueryBuilder($location, search) {

        /**
         * Single query instance
         *
         * @param {string} q Query string query
         */
        function Query(q) {
            var size = 25,
                filters = [];

            /**
             * Set from/size for given query and params
             *
             * @param {Object} query
             * @param {Object} params
             * @returns {Object}
             */
            function paginate(query, params) {
                var page = params.page || 1;
                query.size = size;
                query.from = (page - 1) * query.size;
            }

            /**
             * Get criteria for given query
             */
            this.getCriteria = function getCriteria() {
                var sort = search.getSort();
                var criteria = {
                    query: {filtered: {filter: {and: filters}}},
                    sort: [_.zipObject([sort.field], [sort.dir])]
                };

                var params = $location.search();
                paginate(criteria, params);

                if (q) {
                    criteria.query.filtered.query = {query_string: {query: q}};
                }

                return criteria;
            };

            /**
             * Add filter to query
             *
             * @param {Object} filter
             */
            this.filter = function addFilter(filter) {
                filters.push(filter);
                return this;
            };

            /**
             * Set size
             *
             * @param {number} _size
             */
            this.size = function setSize(_size) {
                size = _size != null ? _size : size;
                return this;
            };

            /**
             * Set query string query
             *
             * @param {string} _q
             */
            this.q = function setQ(_q) {
                q = _q || null;
                return this;
            };

            // do base filtering
            if ($location.search().spike) {
                this.filter({term: {is_spiked: true}});
            } else {
                this.filter({not: {term: {is_spiked: true}}});
            }
        }

        /**
         * Start creating a new query
         *
         * @param {string} q
         */
        this.query = function createQuery(q) {
            return new Query(q);
        };
    }

    angular.module('superdesk.search', ['superdesk.api', 'superdesk.activity'])
        .service('contentQuery', ContentQueryBuilder)
        .service('search', SearchService)

        /**
         * Item filters sidebar
         */
        .directive('sdSearchFacets', function() {
            return {
                templateUrl: 'scripts/superdesk-search/views/search-facets.html',
                link: function(scope) {
                    scope.sTab = true;
                }
            };
        })

        /**
         * Item list with sidebar preview
         */
        .directive('sdSearchResults', function() {
            return {
                templateUrl: 'scripts/superdesk-search/views/search-results.html'
            };
        })

        /**
         * Item search component
         */
        .directive('sdItemSearchbar', function() {
            return {
                templateUrl: 'scripts/superdesk-search/views/item-searchbar.html'
            };
        })

        /**
         * Item sort component
         */
        .directive('sdItemSortbar', function($location, search) {
            return {
                scope: {},
                templateUrl: 'scripts/superdesk-search/views/item-sortbar.html',
                link: function(scope) {
                    scope.sortOptions = search.sortOptions;

                    function getActive() {
                        scope.active = search.getSort();
                    }

                    scope.sort = function sort(field) {
                        search.sort(field);
                    };

                    scope.toggleDir = function toggleDir($event) {
                        search.toggleSortDir();
                    };

                    scope.$on('$routeUpdate', getActive);
                    getActive();
                }
            };
        })

        ;
})();
