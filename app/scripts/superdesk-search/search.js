(function() {
    'use strict';

    SearchService.$inject = ['$location', 'gettext'];
    function SearchService($location, gettext) {
        var sortOptions = [
            {field: 'versioncreated', label: gettext('Updated')},
            {field: 'firstcreated', label: gettext('Created')},
            {field: 'urgency', label: gettext('News Value')}
        ];

        function getSort() {
            var sort = ($location.search().sort || 'versioncreated:desc').split(':');
            return angular.extend(_.find(sortOptions, {field: sort[0]}), {dir: sort[1]});
        }

        function sort(field) {
            var option = _.find(sortOptions, {field: field});
            setSortSearch(option.field, option.defaultDir || 'desc');
        }

        function toggleSortDir() {
            var sort = getSort();
            var dir = sort.dir === 'asc' ? 'desc' : 'asc';
            setSortSearch(sort.field, dir);
        }

        function setSortSearch(field, dir) {
            $location.search('sort', field + ':' + dir);
            $location.search('page', null);
        }

        // sort public api
        this.setSort = sort;
        this.getSort = getSort;
        this.sortOptions = sortOptions;
        this.toggleSortDir = toggleSortDir;

        var cache = {};

        /**
         * Single query instance
         */
        function Query() {
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
            this.getCriteria = function getCriteria(withSource) {
                var search = $location.search();
                var sort = getSort();
                var criteria = {
                    query: {filtered: {filter: {and: filters}}},
                    sort: [_.zipObject([sort.field], [sort.dir])]
                };

                paginate(criteria, search);

                if (search.q) {
                    criteria.query.filtered.query = {query_string: {
                        query: search.q,
                        lenient: false
                    }};
                }

                if (angular.equals(criteria, cache.criteria)) {
                    return cache.criteria;
                }

                if (withSource) {
                    criteria = {source: criteria};
                    if (search.repo) {
                        criteria.repo = search.repo;
                    }
                }

                cache.search = search;
                cache.criteria = criteria;
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

    function SearchController($scope, $location, api, search) {
        $scope.repo = {
            ingest: true,
            archive: true
        };

        function getQuery() {
            return search.query().getCriteria(true);
        }

        function refresh(criteria) {
            api.query('search', criteria).then(function(result) {
                $scope.items = result;
            });
        }

        var query = getQuery();
        $scope.$on('$routeUpdate', function() {
            var next = getQuery();
            if (next !== query) {
                refresh(next);
                query = next;
            }
        });

        refresh(query);
    }

    angular.module('superdesk.search', ['superdesk.api', 'superdesk.activity'])
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
        .directive('sdSearchResults', ['$location', 'preferencesService', function($location, preferencesService) {
            var update = {
                'archive:view': {
                    'allowed': [
                        'mgrid',
                        'compact'
                    ],
                    'category': 'archive',
                    'view': 'mgrid',
                    'default': 'mgrid',
                    'label': 'Users archive view format',
                    'type': 'string'
                }
            };

            return {
                templateUrl: 'scripts/superdesk-search/views/search-results.html',
                link: function(scope) {

                    scope.selected = scope.selected || {};
                    scope.preview = function preview(item) {
                        scope.selected.preview = item;
                        $location.search('_id', item ? item._id : null);
                    };

                    scope.setview = function setView(view) {
                        update['archive:view'].view = view || 'mgrid';
                        preferencesService.update(update, 'archive:view').then(function() {
                            scope.view = view || 'mgrid';
                        });
                    };

                    var savedView;
                    preferencesService.get('archive:view').then(function(result) {
                        savedView = result.view;
                        scope.view = (!!savedView && savedView !== 'undefined') ? savedView : 'mgrid';
                    });
                }
            };
        }])

        /**
         * Item search component
         */
        .directive('sdItemSearchbar', ['$location', function($location) {
            return {
                scope: {repo: '='},
                templateUrl: 'scripts/superdesk-search/views/item-searchbar.html',
                link: function(scope, elem) {
                    var ENTER = 13;

                    var input = elem.find('#search-input');
                    var toggle = elem.find('.dropdown-toggle');
                    var dropdown = elem.find('.dropdown');

                    var params = $location.search();
                    scope.query = params.q;
                    scope.flags = {extended: !!scope.query};

                    scope.meta = {};

                    function getActiveRepos() {
                        var repos = [];
                        angular.forEach(scope.repo, function(val, key) {
                            if (val) {
                                repos.push(key);
                            }
                        });

                        return repos.length ? repos.join(',') : null;
                    }

                    function getQuery() {
                        var metas = [];
                        angular.forEach(scope.meta, function(val, key) {
                            if (val) {
                                metas.push(key + ':(' + val + ')');
                            }
                        });
                        return metas.length ? metas.join(' ') : scope.query || null;
                    }

                    function updateParam() {
                        $location.search('q', getQuery() || null);
                        $location.search('page', null);
                        $location.search('repo', getActiveRepos());
                        scope.query = $location.search().q;
                        scope.meta = {};
                    }

                    scope.search = function() {
                        updateParam();
                        scope.focusOnSearch();
                    };

                    scope.searchOnEnter = function($event) {
                        if ($event.keyCode === ENTER) {
                            scope.search();
                            $event.stopPropagation();
                        }
                    };

                    scope.focusOnSearch = function() {
                        if (_popupOpen()) {
                           toggle.click();
                        }
                        input.focus();
                    };

                    toggle.on('click', function() {
                        if (_popupOpen()) {
                            dropdown.find('.dropdown-menu input').first().focus();
                        }
                    });

                    function _popupOpen() {
                        return dropdown.hasClass('open');
                    }
                }
            };
        }])

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
                        search.setSort(field);
                    };

                    scope.toggleDir = function toggleDir($event) {
                        search.toggleSortDir();
                    };

                    scope.$on('$routeUpdate', getActive);
                    getActive();
                }
            };
        })

        .config(['superdeskProvider', function(superdesk) {
            superdesk.activity('/search', {
                beta: 1,
                priority: 200,
                category: superdesk.MENU_MAIN,
                label: gettext('Search'),
                controller: SearchController,
                templateUrl: 'scripts/superdesk-search/views/search.html'
            });
        }])

        ;
})();
