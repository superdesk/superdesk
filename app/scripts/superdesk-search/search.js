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

    angular.module('superdesk.search', ['superdesk.api', 'superdesk.activity', 'superdesk.desks'])
        .service('search', SearchService)

        /**
         * Item filters sidebar
         */
        .directive('sdSearchFacets', [ '$location', 'desks',  function($location, desks) {
            return {
                estrict: 'A',
                templateUrl: 'scripts/superdesk-search/views/search-facets.html',
                replace: true,
                scope: {
                    items: '=',
                    desk: '='
                },
                link: function(scope, element, attrs) {
                    scope.sTab = true;
                    scope.aggregations = {};
                    scope.selectedFacets = {};
                    scope.keyword = null;

                    var initAggregations = function () {
                        scope.aggregations = {
                            'type': {},
                            'desk': {},
                            'stage': {},
                            'date': {},
                            'source': {},
                            'category': {},
                            'urgency': {},
                            'spiked':{}
                        };
                    };

                    var initSelectedFacets = function () {
                        var search = $location.search();
                        _.forEach(search, function(type, key) {
                            if (key !== 'q' && key !== 'repo' && key !== 'page') {
                                scope.selectedFacets[key] = JSON.parse(type)[0];
                            }
                        });
                    };

                    initSelectedFacets();

                    scope.$watchCollection('items', function() {

                        initAggregations();

                        var search = $location.search();
                        if (scope.keyword !== search.q)
                        {
                            scope.selectedFacets = {};
                            scope.keyword = search.q;
                        }

                        if (scope.items && scope.items._aggregations !== undefined) {

                            _.forEach(scope.items._aggregations.type.buckets, function(type) {
                                if (!scope.selectedFacets.type || scope.selectedFacets.type !== type.key) {
                                    scope.aggregations.type[type.key] = type.doc_count;
                                }
                            });

                            _.forEach(scope.items._aggregations.category.buckets, function(cat) {
                                if (!scope.selectedFacets.category || scope.selectedFacets.category !== cat.key) {
                                    scope.aggregations.category[cat.key] = cat.doc_count;
                                }
                            });

                            _.forEach(scope.items._aggregations.urgency.buckets, function(urgency) {
                                if (!scope.selectedFacets.urgency || scope.selectedFacets.urgency !== urgency.key) {
                                    scope.aggregations.urgency[urgency.key] = urgency.doc_count;
                                }
                            });

                            _.forEach(scope.items._aggregations.source.buckets, function(source) {
                                if (!scope.selectedFacets.source || scope.selectedFacets.source !== source.key) {
                                    scope.aggregations.source[source.key] = source.doc_count;
                                }
                            });

                            _.forEach(scope.items._aggregations.day.buckets, function(day) {
                                if (!scope.selectedFacets.date || scope.selectedFacets.date !== 'Last Day') {
                                    if (day.doc_count > 0) {
                                        scope.aggregations.date['Last Day'] = day.doc_count;
                                    }
                                }
                            });

                            _.forEach(scope.items._aggregations.week.buckets, function(week) {
                                if (!scope.selectedFacets.date || scope.selectedFacets.date !== 'Last Week') {
                                    if (week.doc_count > 0) {
                                        scope.aggregations.date['Last Week'] = week.doc_count;
                                    }
                                }
                            });

                            _.forEach(scope.items._aggregations.month.buckets, function(month) {
                                if (!scope.selectedFacets.date || scope.selectedFacets.date !== 'Last Month') {
                                    if (month.doc_count > 0) {
                                        scope.aggregations.date['Last Month'] = month.doc_count;
                                    }
                                }
                            });

                            if (!scope.desk) {
                                _.forEach(scope.items._aggregations.desk.buckets, function(desk) {
                                    if (!scope.selectedFacets.desk || scope.selectedFacets.desk !== desks.deskLookup[desk.key].name) {
                                        scope.aggregations.desk[desks.deskLookup[desk.key].name] = desk.doc_count;
                                    }
                                }) ;
                            }

                            if (scope.desk) {
                                _.forEach(scope.items._aggregations.stage.buckets, function(stage) {
                                    _.forEach(desks.deskStages[desks.activeDeskId], function(deskStage) {
                                        if (!scope.selectedFacets.stage || scope.selectedFacets.stage !== deskStage.name) {
                                            if (deskStage._id === stage.key) {
                                                scope.aggregations.stage[deskStage.name] = stage.doc_count;
                                            }
                                        }
                                    });
                                });
                            }
                        }
                    });

                    scope.setFilter = function(type, key) {

                        scope.selectedFacets[type] = key;

                        if (!scope.isEmpty(type) && key) {
                            $location.search(type, JSON.stringify([key]));
                        } else {
                            $location.search(type, null);
                        }
                    };

                    scope.setDateFilter = function(key) {
                        scope.selectedFacets.date = key;
                        var d = new Date();

                        if (key === 'Last Day') {
                            d.setDate(d.getDate() - 1);
                            $location.search('after', scope.format(d));
                        } else if (key === 'Last Week'){
                            d.setDate(d.getDate() - 7);
                             $location.search('after', scope.format(d));
                        } else if (key === 'Last Month'){
                            d.setDate(d.getDate() - 30);
                             $location.search('after', scope.format(d));
                        } else {
                            $location.search('after', null);
                        }
                    };

                    scope.removeFilter = function(type, key) {
                        if (key.indexOf('Last') >= 0) {
                            scope.removeDateFilter(key);
                        } else {
                            var search = $location.search();
                            if (search[type]) {
                                var keys = JSON.parse(search[type]);
                                keys.splice(keys.indexOf(key), 1);
                                if (keys.length > 0)
                                {
                                    $location.search(type, JSON.stringify(keys));
                                } else {
                                    $location.search(type, null);
                                }
                            }
                            delete scope.selectedFacets[type];
                        }
                    };

                    scope.removeDateFilter = function(key) {

                        var search = $location.search();
                        if (search.after) {
                            $location.search('after', null);
                        }

                        delete scope.selectedFacets.date;
                    };

                    scope.isEmpty = function(type) {
                        return _.isEmpty(scope.aggregations[type]);
                    };

                    scope.format = function (date) {
                        return date ? moment(date).format('YYYY-MM-DD') : null; // jshint ignore:line
                    };
                }
            };
        }])
        /**
         * Urgency Filter
         */
        .directive('sdFilterUrgency', ['$location', function($location) {
            return {
                scope: true,
                link: function($scope, element, attrs) {

                    $scope.urgency = {
                        min: '1',
                        max: '5'
                    };

                    /*  $scope.urgency = {
                        min: $location.search().urgency_min || 1,
                        max: $location.search().urgency_max || 5
                    };*/

                    function handleUrgency(urgency) {
                        var min = Math.round(urgency.min);
                        var max = Math.round(urgency.max);
                        if (min !== 1 || max !== 5) {
                            var urgency_norm = {
                                min: min,
                                max: max
                            };
                            $location.search('urgency_min', urgency_norm.min);
                            $location.search('urgency_max', urgency_norm.max);
                        } else {
                            $location.search('urgency_min', null);
                            $location.search('urgency_max', null);
                        }

                    }

                    var handleUrgencyWrap = _.throttle(handleUrgency, 2000);

                    $scope.$watchCollection('urgency', function(newVal) {
                        handleUrgencyWrap(newVal);
                    });
                }
            };
        }])

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
                        $location.$$search = {};
                        $location.search('q', getQuery() || null);
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
