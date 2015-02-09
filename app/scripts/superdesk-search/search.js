(function() {
    'use strict';

    SearchService.$inject = ['$location', 'gettext'];
    function SearchService($location, gettext) {
        var sortOptions = [
            {field: 'versioncreated', label: gettext('Updated')},
            {field: 'firstcreated', label: gettext('Created')},
            {field: 'urgency', label: gettext('News Value')},
            {field: 'anpa-category.name', label: gettext('Category')},
            {field: 'slugline', label: gettext('Keyword')},
            {field: 'priority', label: gettext('Priority')}
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

        /**
         * Single query instance
         */
        function Query(q) {
            var DEFAULT_SIZE = 25,
                size,
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
                var pagesize = size || Number(localStorage.getItem('pagesize')) || Number(params.max_results) || DEFAULT_SIZE;
                query.size = pagesize;
                query.from = (page - 1) * query.size;
            }

            function buildFilters(params, query) {

                if (params.beforefirstcreated || params.afterfirstcreated) {
                    var range = {firstcreated: {}};
                    if (params.beforefirstcreated) {
                        range.firstcreated.lte = params.beforefirstcreated;
                    }

                    if (params.afterfirstcreated) {
                        range.firstcreated.gte = params.afterfirstcreated;
                    }

                    query.filter({range: range});
                }

                if (params.beforeversioncreated || params.afterversioncreated) {
                    var vrange = {versioncreated: {}};
                    if (params.beforeversioncreated) {
                        vrange.versioncreated.lte = params.beforeversioncreated;
                    }

                    if (params.afterversioncreated) {
                        vrange.versioncreated.gte = params.afterversioncreated;
                    }

                    query.filter({range: vrange});
                }

                if (params.after)
                {
                    var facetrange = {firstcreated: {}};
                    facetrange.firstcreated.gte = params.after;
                    query.filter({range: facetrange});
                }

                if (params.type) {
                    var type = {
                        type: JSON.parse(params.type)
                    };
                    query.filter({terms: type});
                }

                if (params.urgency) {
                    query.filter({term: {urgency: JSON.parse(params.urgency)}});
                }

                if (params.source) {
                    query.filter({term: {source: JSON.parse(params.source)}});
                }

                if (params.category) {
                    query.filter({term: {'anpa-category.name': JSON.parse(params.category)}});
                }

                if (params.desk) {
                    query.filter({term: {'task.desk': JSON.parse(params.desk)}});
                }

                if (params.stage) {
                    query.filter({term: {'task.stage': JSON.parse(params.stage)}});
                }

                if (params.state) {
                    query.filter({term: {'state': JSON.parse(params.state)}});
                }
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

                if (search.q || q) {
                    criteria.query.filtered.query = {query_string: {
                        query: search.q || q,
                        lenient: false,
                        default_operator: 'AND'
                    }};
                }

                if (withSource) {
                    criteria = {source: criteria};
                    if (search.repo) {
                        criteria.repo = search.repo;
                    }
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

            // do base filtering
            if ($location.search().spike) {
                this.filter({term: {state: 'spiked'}});
            } else {
                this.filter({not: {term: {state: 'spiked'}}});
            }

            buildFilters($location.search(), this);
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

    SearchController.$inject = ['$scope', '$location', 'api', 'search'];
    function SearchController($scope, $location, api, search) {

        $scope.context = 'search';

        $scope.repo = {
            ingest: true,
            archive: true
        };

        function refresh() {
            var query = _.omit($location.search(), '_id');
            if (!_.isEqual(_.omit(query, 'page'), _.omit(oldQuery, 'page'))) {
                $location.search('page', null);
            }

            var criteria = search.query().getCriteria(true);
            api.query('search', criteria).then(function(result) {
                $scope.items = result;
            });

            oldQuery =  query;
        }

        var oldQuery = _.omit($location.search(), '_id');
        $scope.$watch(function getSearchParams() {
            return _.omit($location.search(), '_id');
        }, refresh, true);
    }

    angular.module('superdesk.search', ['superdesk.api', 'superdesk.activity', 'superdesk.desks'])
        .service('search', SearchService)
        .filter('FacetLabels', function() {
            return function(input) {
                if (input.toUpperCase() === 'URGENCY') {
                    return 'News Value';
                } else {
                    return input;
                }

            };
        })
        /**
         * Item filters sidebar
         */
        .directive('sdSearchFacets', ['$location', 'desks',  function($location, desks) {
            desks.initialize();
            return {
                require: '^sdSearchContainer',
                templateUrl: 'scripts/superdesk-search/views/search-facets.html',
                scope: {
                    items: '=',
                    desk: '='
                },
                link: function(scope, element, attrs, controller) {
                    scope.flags = controller.flags;
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
                            'state':{}
                        };
                    };

                    var FacetKeys = {
                        'type': 1,
                        'category': 1,
                        'urgency': 1,
                        'source': 1,
                        'day': 1,
                        'week': 1,
                        'month': 1,
                        'desk': 1,
                        'stage':1,
                        'state':1
                    };

                    var initSelectedFacets = function () {
                        return desks.initialize().then(function(result) {
                            var search = $location.search();
                            scope.keyword = search.q;
                            _.forEach(search, function(type, key) {
                                if (key === 'desk') {
                                    scope.selectedFacets[key] = desks.deskLookup[JSON.parse(type)[0]].name;
                                } else if (key === 'stage') {
                                    var stageid = type;
                                    _.forEach(desks.deskStages[desks.activeDeskId], function(deskStage) {
                                        if (deskStage._id === JSON.parse(stageid)[0]) {
                                            scope.selectedFacets[key] = deskStage.name;
                                        }
                                    });
                                } else if (FacetKeys[key]) {
                                    scope.selectedFacets[key] = JSON.parse(type)[0];
                                }
                            });
                        });
                    };

                    scope.$watch('items', function() {

                        initAggregations();
                        initSelectedFacets().then(function() {
                            var search = $location.search();
                            if (search.q && scope.keyword !== search.q)
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
                                    if ((!scope.selectedFacets.category || scope.selectedFacets.category !== cat.key) && cat.key !== '') {
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

                                _.forEach(scope.items._aggregations.state.buckets, function(state) {
                                    if (!scope.selectedFacets.state || scope.selectedFacets.state !== state.key) {
                                        scope.aggregations.state[state.key] = state.doc_count;
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
                                            scope.aggregations.desk[desks.deskLookup[desk.key].name] = {
                                                count: desk.doc_count,
                                                id: desk.key
                                            };
                                        }
                                    }) ;
                                }

                                if (scope.desk) {
                                    _.forEach(scope.items._aggregations.stage.buckets, function(stage) {
                                        _.forEach(desks.deskStages[scope.desk._id], function(deskStage) {
                                            if (!scope.selectedFacets.stage || scope.selectedFacets.stage !== deskStage.name) {
                                                if (deskStage._id === stage.key) {
                                                    scope.aggregations.stage[deskStage.name] = {count: stage.doc_count, id: stage.key};
                                                }
                                            }
                                        });
                                    });
                                }
                            }
                        });
                    });

                    var setSelectedFacets = function(type, key) {
                        if (type === 'desk') {
                            scope.selectedFacets[type] = desks.deskLookup[key].name;
                        } else if (type === 'stage') {
                            _.forEach(desks.deskStages[desks.activeDeskId], function(deskStage) {
                                if (deskStage._id === key) {
                                    scope.selectedFacets[type] = deskStage.name;
                                }
                            });
                        } else {
                            scope.selectedFacets[type] = key;
                        }
                    };

                    scope.setFilter = function(type, key) {

                        setSelectedFacets(type, key);

                        if (!scope.isEmpty(type) && key) {
                            $location.search(type, JSON.stringify([key]));
                        } else {
                            $location.search(type, null);
                        }
                    };

                    scope.setDateFilter = function(key) {
                        scope.selectedFacets.date = key;

                        if (key === 'Last Day') {
                            $location.search('after', 'now-24H');
                        } else if (key === 'Last Week'){
                             $location.search('after', 'now-1w');
                        } else if (key === 'Last Month'){
                             $location.search('after', 'now-1M');
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
                require: '^sdSearchContainer',
                templateUrl: 'scripts/superdesk-search/views/search-results.html',
                link: function(scope, elem, attr, controller) {

                    var multiSelectable = (attr.multiSelectable === undefined) ? false : true;

                    scope.flags = controller.flags;
                    scope.selected = scope.selected || {};

                    scope.preview = function preview(item) {
                        if (multiSelectable) {
                            if (_.findIndex(scope.selectedList, {_id: item._id}) === -1) {
                                scope.selectedList.push(item);
                            } else {
                                _.remove(scope.selectedList, {_id: item._id});
                            }
                        }
                        scope.selected.preview = item;
                        $location.search('_id', item ? item._id : null);
                    };

                    scope.openLightbox = function openLightbox() {
                        scope.selected.view = scope.selected.preview;
                    };

                    scope.closeLightbox = function closeLightbox() {
                        scope.selected.view = null;
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

        .directive('sdSearchWithin', ['$location', function($location) {
            return {
                scope: {},
                templateUrl: 'scripts/superdesk-search/views/search-within.html',
                link: function(scope, elem) {
                    scope.searchWithin = function() {
                        if (scope.within) {
                            var params = $location.search();
                            if (params.q) {
                                scope.query = params.q + ' ' + scope.within;
                            } else {
                                scope.query = scope.within;
                            }
                            $location.search('q', scope.query|| null);
                            scope.within = null;
                        }
                    };
                }
            };
        }])

        .directive('sdItemContainer', ['$filter', 'desks', 'api', function($filter, desks, api) {
            return {
                scope: {
                    item: '='
                },
                template: '{{item.container}}',
                link: function(scope, elem) {

                    if (scope.item._type !== 'ingest') {
                        if (scope.item.task && scope.item.task.desk) {
                            desks.initialize().then(function() {
                                scope.item.container = 'desk:' + desks.deskLookup[scope.item.task.desk].name ;
                            });
                        } else {
                            scope.item.container = 'location:workspace';
                        }
                    }
                }
            };
        }])

        /**
         * Open Item dialog
         */
        .directive('sdItemGlobalsearch', ['superdesk', 'session', '$location', 'search', 'api', 'notify', 'gettext', 'keyboardManager',
            function(superdesk, session, $location, search, api, notify, gettext, keyboardManager) {
            return {
                scope: {repo: '=', context: '='},
                templateUrl: 'scripts/superdesk-search/views/item-globalsearch.html',
                link: function(scope, elem) {

                    var ENTER = 13;
                    var ESC = 27;
                    scope.meta = {};
                    scope.flags = {enabled: false};
                    var opt = {global: true};
                    keyboardManager.bind('ctrl+0', function() {
                        scope.flags.enabled = true;
                    }, opt);
                    keyboardManager.bind('esc', function() {
                        scope.flags.enabled = false;
                    }, opt);

                    function reset() {
                        scope.meta.unique_name = '';
                    }

                    function openItem(items) {
                        if (items.length > 0) {
                            reset();
                            scope.flags.enabled = false;
                            if (items[0].type === 'composite') {
                                superdesk.intent('author', 'package', items[0]);
                            } else {
                                superdesk.intent('author', 'article', items[0]);
                            }
                        } else {
                            notify.error(gettext('Item not found...'));
                            scope.flags.enabled = true;
                        }
                    }
                    function searchUserContent(criteria) {
                           var resource = api('user_content', session.identity);
                           resource.query(criteria).then(function(result) {
                                    openItem(result._items);
                            }, function(response) {
                                scope.message = gettext('There was a problem, item can not open.');
                            });
                    }
                    function fetchItem() {
                        var filter = [
                            {not: {term: {state: 'spiked'}}},
                            {term: {unique_name: scope.meta.unique_name}}
                        ];
                        var criteria = {
                                            repo: 'ingest,archive',
                                            source: {
                                            query: {filtered: {filter: {
                                                and: filter
                                            }}}
                                         }
                        };
                        api.query('search', criteria).then(function(result) {
                                scope.items = result._items;
                                if (scope.items.length > 0) {
                                    openItem(scope.items);
                                    reset();
                                } else {
                                    searchUserContent(criteria);
                                }
                        }, function(response) {
                            scope.message = gettext('There was a problem, item can not open.');
                        });
                    }

                    scope.search = function() {
                        fetchItem();
                    };
                    scope.openOnEnter = function($event) {
                        if ($event.keyCode === ENTER) {
                            scope.search();
                            $event.stopPropagation();
                        }
                        if ($event.keyCode === ESC) {
                            _closeDialog();
                        }
                    };

                    scope.close = function() {
                        _closeDialog();
                    };

                    function _closeDialog() {
                        reset();
                        scope.flags.enabled = false;
                    }
                }
            };
        }])
        /**
         * Item search component
         */
        .directive('sdItemSearchbar', ['$location', function($location) {
            return {
                scope: {repo: '=', context: '='},
                templateUrl: 'scripts/superdesk-search/views/item-searchbar.html',
                link: function(scope, elem) {
                    var ENTER = 13;
                    var ESC = 27;

                    var input = elem.find('#search-input');
                    scope.advancedOpen = false;

                    function init() {
                        var params = $location.search();
                        scope.query = params.q;
                        scope.flags = false;
                        scope.meta = {};

                        if (params.repo) {
                            scope.repo.archive = params.repo.indexOf('archive') >= 0;
                            scope.repo.ingest = params.repo.indexOf('ingest') >= 0;
                        }
                    }

                    init();

                    scope.$on('$locationChangeSuccess', function() {
                        if (scope.query !== $location.search().q) {
                            init();
                        }
                    });

                    function getActiveRepos() {
                        var repos = [];
                        angular.forEach(scope.repo, function(val, key) {
                            if (val) {
                                repos.push(key);
                            }
                        });

                        return repos.length ? repos.join(',') : null;
                    }

                    function getFirstKey(data) {
                        for (var prop in data) {
                            if (data.hasOwnProperty(prop)) {
                                return prop;
                            }
                        }
                    }

                    function getQuery() {
                        var metas = [];
                        angular.forEach(scope.meta, function(val, key) {
                            if (key === '_all') {
                                metas.push(val.join(' '));
                            } else {
                                if (val) {
                                    if (typeof(val) === 'string'){
                                        if (val) {
                                            metas.push(key + ':(' + val + ')');
                                        }
                                    } else {
                                        var subkey = getFirstKey(val);
                                        if (val[subkey]) {
                                            metas.push(key + '.' + subkey + ':(' + val[subkey] + ')');
                                        }
                                    }
                                }
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

                    function parseFields() {
                        scope.meta = {};
                        if (scope.query) {
                           angular.forEach(scope.query.split(' '), function(val) {
                                if (val.indexOf(':') >= 0) {
                                    var meta = val.split(':')[0];
                                    var value = val.split(':')[1].replace('(', '').replace(')', '');

                                    if (meta.indexOf('.') >= 0) {
                                        var submeta = meta.split('.')[0];
                                        var subvalue = meta.split('.')[1];
                                        scope.meta[submeta] = {};
                                        scope.meta[submeta][subvalue] = value;
                                    } else {
                                        scope.meta[meta] = value;
                                    }
                                } else {
                                    if (!scope.meta._all) {
                                        scope.meta._all = [];
                                    }
                                    scope.meta._all.push(val);
                                }
                            });
                        }
                    }

                    scope.search = function() {
                        updateParam();
                        _closeSearchPopup();
                    };

                    scope.searchOnEnter = function($event) {
                        if ($event.keyCode === ENTER) {
                            scope.search();
                            $event.stopPropagation();
                        }
                        if ($event.keyCode === ESC) {
                            _closeSearchPopup();
                        }
                    };

                    scope.focusOnSearch = function() {
                        if (scope.advancedOpen) {
                           scope.toggle();
                        }
                        input.focus();
                    };

                    scope.toggle = function() {
                        scope.advancedOpen = !scope.advancedOpen;
                        if (scope.advancedOpen) {
                            parseFields();
                        }
                    };

                    function _closeSearchPopup() {
                        scope.flags.extended = false;
                    }
                }
            };
        }])

        /**
         * Item sort component
         */
        .directive('sdItemSortbar', ['$location', 'search', function sortBarDirective($location, search) {
            return {
                scope: {},
                templateUrl: 'scripts/superdesk-search/views/item-sortbar.html',
                link: function(scope) {
                    scope.sortOptions = search.sortOptions;

                    function getActive() {
                        scope.active = search.getSort();
                        var srch = $location.search();
                        if (srch.q && srch.q !== '') {
                            scope.queryString = srch.q;
                        } else {
                            scope.queryString = null;
                        }
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
        }])

        .directive('sdSavedSearches', ['api', 'session', '$location', 'notify', 'gettext',
        function(api, session, $location, notify, gettext) {
            return {
                templateUrl: 'scripts/superdesk-search/views/saved-searches.html',
                scope: {},
                link: function(scope) {

                    var resource = api('saved_searches', session.identity);
                    scope.selected = null;
                    scope.editSearch = null;

                    resource.query().then(function(views) {
                        scope.views = views._items;
                    });

                    scope.select = function(view) {
                        scope.selected = view;
                        $location.search(view.filter.query);
                    };

                    scope.edit = function() {
                        scope.editSearch = {};
                    };

                    scope.cancel = function() {
                        scope.editSearch = null;
                    };

                    scope.save = function(editSearch) {

                        editSearch.filter = {query: $location.search()};

                        resource.save({}, editSearch)
                        .then(function(result) {
                            notify.success(gettext('Saved search created'));
                            scope.cancel();
                            scope.views.push(result);
                        }, function() {
                            notify.error(gettext('Error. Saved search not created.'));
                        });
                    };

                    scope.remove = function(view) {
                        resource.remove(view).then(function() {
                            notify.success(gettext('Saved search removed'));
                            _.remove(scope.views, {_id: view._id});
                        }, function() {
                            notify.error(gettext('Error. Saved search not deleted.'));
                        });
                    };
                }
            };
        }])

        .directive('sdSearchContainer', function() {
            return {
                controller: ['$scope', function SearchContainerController($scope) {
                    this.flags = $scope.flags || {};
                }]
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
