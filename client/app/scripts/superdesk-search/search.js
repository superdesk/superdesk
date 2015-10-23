(function() {
    'use strict';

    SearchService.$inject = ['$location', 'gettext'];
    function SearchService($location, gettext) {
        var sortOptions = [
            {field: 'versioncreated', label: gettext('Updated')},
            {field: 'firstcreated', label: gettext('Created')},
            {field: 'urgency', label: gettext('News Value')},
            {field: 'anpa_category.name', label: gettext('Category')},
            {field: 'slugline', label: gettext('Slugline')},
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

        /*
         * Sets the from-to desk filters.
         */
        function setFromToDeskFilters(filters, params) {
            var from_desk = params.from_desk,
                to_desk = params.to_desk,
                desk;

            if (from_desk) {
                desk = from_desk.split('-');
                if (desk.length === 2) {
                    if (desk[1] === 'authoring') {
                        filters.push({'term': {'task.last_authoring_desk': desk[0]}});
                    } else {
                        filters.push({'term': {'task.last_production_desk': desk[0]}});
                    }

                }
            }

            if (to_desk) {
                desk = to_desk.split('-');
                if (desk.length === 2) {
                    filters.push({'term': {'task.desk': desk[0]}});
                    if (!from_desk) {
                        var field = desk[1] === 'authoring' ? 'task.last_production_desk' : 'task.last_authoring_desk';
                        filters.push({'exists': {'field': field}});
                    }
                }
            }
        }

        /*
         * Function for finding object by string array for subject codes
         */
        this.getSubjectCodes = function (currentTags, subjectcodes) {
            var queryArray = currentTags.selectedParameters, filteredArray = [];
            if (!$location.search().q) {
                return filteredArray;
            }
            for (var i = 0, queryArrayLength = queryArray.length; i < queryArrayLength; i++) {
                var queryArrayElement = queryArray[i];
                if (queryArrayElement.indexOf('subject.name') !== -1) {
                    var elementName = queryArrayElement.substring(
                            queryArrayElement.lastIndexOf('(') + 1,
                            queryArrayElement.lastIndexOf(')')
                            );
                    for (var j = 0, subjectCodesLength = subjectcodes.length; j < subjectCodesLength; j++) {
                        if (subjectcodes[j].name === elementName) {
                            filteredArray.push(subjectcodes[j]);
                        }
                    }
                }
            }
            return filteredArray;
        };

        // sort public api
        this.setSort = sort;
        this.getSort = getSort;
        this.sortOptions = sortOptions;
        this.toggleSortDir = toggleSortDir;

        /**
         * Single query instance
         */
        function Query(params) {
            var size,
                filters = [],
                post_filters = [];

            if (params == null) {
                params = {};
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

                    query.post_filter({range: range});
                }

                if (params.beforeversioncreated || params.afterversioncreated) {
                    var vrange = {versioncreated: {}};
                    if (params.beforeversioncreated) {
                        vrange.versioncreated.lte = params.beforeversioncreated;
                    }

                    if (params.afterversioncreated) {
                        vrange.versioncreated.gte = params.afterversioncreated;
                    }

                    query.post_filter({range: vrange});
                }

                if (params.after)
                {
                    var facetrange = {firstcreated: {}};
                    facetrange.firstcreated.gte = params.after;
                    query.post_filter({range: facetrange});
                }

                if (params.type) {
                    var type = {
                        type: JSON.parse(params.type)
                    };
                    query.post_filter({terms: type});
                }

                if (params.urgency) {
                    query.post_filter({terms: {urgency: JSON.parse(params.urgency)}});
                }

                if (params.priority) {
                    query.post_filter({terms: {priority: JSON.parse(params.priority)}});
                }

                if (params.source) {
                    query.post_filter({terms: {source: JSON.parse(params.source)}});
                }

                if (params.credit && params.creditqcode) {
                    query.post_filter({terms: {credit: JSON.parse(params.creditqcode)}});
                }

                if (params.category) {
                    query.post_filter({terms: {'anpa_category.name': JSON.parse(params.category)}});
                }

                if (params.desk) {
                    query.post_filter({terms: {'task.desk': JSON.parse(params.desk)}});
                }

                if (params.stage) {
                    query.post_filter({terms: {'task.stage': JSON.parse(params.stage)}});
                }
            }

            /**
             * Get criteria for given query
             */
            this.getCriteria = function getCriteria(withSource) {
                var search = params;
                var sort = getSort();
                setFromToDeskFilters(filters, params);
                var criteria = {
                    query: {filtered: {filter: {and: filters}}},
                    sort: [_.zipObject([sort.field], [sort.dir])]
                };

                if (post_filters.length > 0) {
                    criteria.post_filter = {'and': post_filters};
                }

                if (search.q) {
                    criteria.query.filtered.query = {query_string: {
                        query: search.q,
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

            this.post_filter = function addPostFilter(filter) {
                post_filters.push(filter);
                return this;
            };

            this.clear_filters = function clearFilters() {
                filters = [];
                post_filters = [];
                buildFilters({}, this);
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
            if (params.spike) {
                this.filter({term: {state: 'spiked'}});
            } else {
                this.filter({not: {term: {state: 'spiked'}}});
            }

            if (params.ignoreKilled) {
                this.filter({not: {term: {state: 'killed'}}});
            }

            if (params.onlyLastPublished) {
                this.filter({not: {term: {last_published_version: 'false'}}});
            }

            if (params.ignoreDigital) {
                this.filter({not: {term: {package_type: 'takes'}}});
            }

            if (params.ignoreScheduled) {
                this.filter({not: {term: {state: 'scheduled'}}});
            }

            // remove the older version of digital package as part for base filtering.
            this.filter({not: {and: [{term: {_type: 'published'}},
                {term: {package_type: 'takes'}},
                {term: {last_published_version: false}}]}});

            //remove the digital package from production view.
            this.filter({not: {and: [{term: {package_type: 'takes'}}, {term: {_type: 'archive'}}]}});

            buildFilters(params, this);
        }

        /**
         * Start creating a new query
         *
         * @param {Object} params
         */
        this.query = function createQuery(params) {
            return new Query(params);
        };
    }

    TagService.$inject = ['$location', 'desks'];
    function TagService($location, desks) {
        var tags = {};
        tags.selectedFacets = {};
        tags.selectedParameters = [];
        tags.selectedKeywords = [];
        tags.currentSearch = {};

        var FacetKeys = {
            'type': 1,
            'category': 1,
            'urgency': 1,
            'priority': 1,
            'source': 1,
            'credit': 1,
            'day': 1,
            'week': 1,
            'month': 1,
            'desk': 1,
            'stage':1
        };

        function initSelectedParameters (parameters) {
            tags.selectedParameters = [];
            while (parameters.indexOf(':') > 0 &&
                   parameters.indexOf(':') < parameters.indexOf('(') &&
                   parameters.indexOf(':') < parameters.indexOf(')')) {

                var colonIndex = parameters.indexOf(':');
                var parameter = parameters.substring(parameters.lastIndexOf(' ', colonIndex), parameters.indexOf(')', colonIndex) + 1);

                tags.selectedParameters.push(parameter);
                parameters = parameters.replace(parameter, '');
            }

            return parameters;
        }

        function initSelectedKeywords (keywords) {
            tags.selectedKeywords = [];
            while (keywords.indexOf('(') >= 0) {
                var parenthesisIndex = keywords.indexOf('(');
                var keyword = keywords.substring(parenthesisIndex, keywords.indexOf(')', parenthesisIndex) + 1);
                tags.selectedKeywords.push(keyword);
                keywords = keywords.replace(keyword, '');
            }
        }

        function initFromToDesk(params) {
            if (params.from_desk) {
                tags.selectedParameters.push('From Desk:' + desks.deskLookup[params.from_desk.split('-')[0]].name);
            }
            if (params.to_desk) {
                tags.selectedParameters.push('To Desk:' + desks.deskLookup[params.to_desk.split('-')[0]].name);
            }
        }

        function removeFacet (type, key) {
            if (key.indexOf('Last') >= 0) {
                removeDateFacet();
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
                    if (type === 'credit') {
                        $location.search('creditqcode', null);
                    }
                }
            }
        }

        function removeDateFacet () {
            var search = $location.search();
            if (search.after) {
                $location.search('after', null);
            }
        }

        function initSelectedFacets () {
            return desks.initialize().then(function(result) {
                tags.selectedFacets = {};
                tags.selectedParameters = [];
                tags.selectedKeywords = [];

                tags.currentSearch = $location.search();

                var parameters = tags.currentSearch.q;
                if (parameters) {
                    var keywords = initSelectedParameters(parameters);
                    initSelectedKeywords(keywords);
                }

                initFromToDesk(tags.currentSearch);

                _.forEach(tags.currentSearch, function(type, key) {
                    if (key !== 'q') {
                        tags.selectedFacets[key] = [];

                        if (key === 'desk') {
                            var selectedDesks = JSON.parse(type);
                            _.forEach(selectedDesks, function(selectedDesk) {
                                tags.selectedFacets[key].push(desks.deskLookup[selectedDesk].name);
                            });
                        } else if (key === 'stage') {
                            var stageid = type;
                            _.forEach(desks.deskStages[desks.getCurrentDeskId()], function(deskStage) {
                                if (deskStage._id === JSON.parse(stageid)[0]) {
                                    tags.selectedFacets[key].push(deskStage.name);
                                }
                            });
                        } else if (key === 'after') {

                            if (type === 'now-24H') {
                                tags.selectedFacets.date = ['Last Day'];
                            } else if (type === 'now-1w'){
                                tags.selectedFacets.date = ['Last Week'];
                            } else if (type === 'now-1M'){
                                tags.selectedFacets.date = ['Last Month'];
                            }

                        } else if (FacetKeys[key]) {
                            tags.selectedFacets[key] = JSON.parse(type);
                        }
                    }
                });

                return tags;
            });
        }

        return {
            initSelectedFacets: initSelectedFacets,
            removeFacet: removeFacet
        };
    }

    angular.module('superdesk.search', [
        'superdesk.api',
        'superdesk.desks',
        'superdesk.activity',
        'superdesk.list',
        'superdesk.keyboard'
    ])
        .service('search', SearchService)
        .service('tags', TagService)
        .controller('MultiActionBar', MultiActionBarController)
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
         * A directive that generates the sidebar containing search results
         * filters (so-called "aggregations" in Elastic's terms).
         */
        .directive('sdSearchFacets', ['$location', 'desks', 'privileges', 'tags', 'asset',
            function($location, desks, privileges, tags, asset) {
            desks.initialize();
            return {
                require: '^sdSearchContainer',
                templateUrl: asset.templateUrl('superdesk-search/views/search-facets.html'),
                scope: {
                    items: '=',
                    desk: '=',
                    repo: '=',
                    context: '='
                },
                link: function(scope, element, attrs, controller) {
                    scope.flags = controller.flags;
                    scope.sTab = true;
                    scope.aggregations = {};
                    scope.privileges = privileges.privileges;

                    var initAggregations = function () {
                        scope.aggregations = {
                            'type': {},
                            'desk': {},
                            'stage': {},
                            'date': {},
                            'source': {},
                            'credit': {},
                            'category': {},
                            'urgency': {},
                            'priority': {}
                        };
                    };

                    scope.$watch('items', function() {

                        initAggregations();

                        tags.initSelectedFacets().then(function(currentTags) {

                            scope.tags = currentTags;

                            if (!scope.items || scope.items._aggregations === undefined) {
                                return;
                            }

                            _.forEach(scope.items._aggregations.type.buckets, function(type) {
                                scope.aggregations.type[type.key] = type.doc_count;
                            });

                            _.forEach(scope.items._aggregations.category.buckets, function(cat) {
                                if (cat.key !== '') {
                                    scope.aggregations.category[cat.key] = cat.doc_count;
                                }
                            });

                            if (angular.isDefined(scope.items._aggregations.urgency))
                            {
                                _.forEach(scope.items._aggregations.urgency.buckets, function(urgency) {
                                    scope.aggregations.urgency[urgency.key] = urgency.doc_count;
                                });
                            }

                            _.forEach(scope.items._aggregations.priority.buckets, function(priority) {
                                scope.aggregations.priority[priority.key] = priority.doc_count;
                            });

                            _.forEach(scope.items._aggregations.source.buckets, function(source) {
                                scope.aggregations.source[source.key] = source.doc_count;
                            });
                            if (angular.isDefined(scope.items._aggregations.source))
                            {
                                _.forEach(scope.items._aggregations.source.buckets, function(source) {
                                    scope.aggregations.source[source.key] = source.doc_count;
                                });
                            }

                            if (angular.isDefined(scope.items._aggregations.credit))
                            {
                                _.forEach(scope.items._aggregations.credit.buckets, function(credit) {
                                    scope.aggregations.credit[credit.key] = {'count': credit.doc_count, 'qcode': credit.qcode};
                                });
                            }

                            _.forEach(scope.items._aggregations.day.buckets, function(day) {
                                scope.aggregations.date['Last Day'] = day.doc_count;
                            });

                            _.forEach(scope.items._aggregations.week.buckets, function(week) {
                                scope.aggregations.date['Last Week'] = week.doc_count;
                            });

                            _.forEach(scope.items._aggregations.month.buckets, function(month) {
                                scope.aggregations.date['Last Month'] = month.doc_count;
                            });

                            if (!scope.desk && angular.isDefined(scope.items._aggregations.stage)) {
                                _.forEach(scope.items._aggregations.desk.buckets, function(desk) {
                                    var lookedUpDesk = desks.deskLookup[desk.key];

                                    if (typeof lookedUpDesk === 'undefined') {
                                        var msg =  [
                                            'Desk (key: ', desk.key, ') not found in ',
                                            'deskLookup, probable storage inconsistency.'
                                        ].join('');
                                        console.warn(msg);
                                        return;
                                    }

                                    scope.aggregations.desk[lookedUpDesk.name] = {
                                            count: desk.doc_count,
                                            id: desk.key
                                        };
                                });
                            }

                            if (scope.desk && angular.isDefined(scope.items._aggregations.stage)) {
                                _.forEach(scope.items._aggregations.stage.buckets, function(stage) {
                                    _.forEach(desks.deskStages[scope.desk._id], function(deskStage) {
                                        if (deskStage._id === stage.key) {
                                            scope.aggregations.stage[deskStage.name] = {count: stage.doc_count, id: stage.key};
                                        }
                                    });
                                });
                            }

                        });
                    });

                    scope.toggleFilter = function(type, key) {
                        if (scope.hasFilter(type, key)) {
                            scope.removeFilter(type, key);
                        } else {
                            if (type === 'date') {
                                scope.setDateFilter(key);
                            } else {
                                scope.setFilter(type, key);
                            }
                        }
                    };

                    scope.removeFilter = function(type, key) {
                        tags.removeFacet(type, key);
                    };

                    scope.setFilter = function(type, key) {
                        if (!scope.isEmpty(type) && key) {
                            var currentKeys = $location.search()[type];
                            if (currentKeys) {
                                currentKeys = JSON.parse(currentKeys);
                                currentKeys.push(key);
                                $location.search(type, JSON.stringify(currentKeys));
                            } else {
                                if (type === 'credit') {
                                    $location.search('creditqcode',
                                        JSON.stringify([scope.aggregations.credit[key].qcode]));
                                }
                                $location.search(type, JSON.stringify([key]));
                            }
                        } else {
                            $location.search(type, null);
                        }
                    };

                    scope.setDateFilter = function(key) {
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

                    scope.isEmpty = function(type) {
                        return _.isEmpty(scope.aggregations[type]);
                    };

                    scope.format = function (date) {
                        return date ? moment(date).format('YYYY-MM-DD') : null; // jshint ignore:line
                    };

                    scope.hasFilter = function(type, key) {
                        if (type === 'desk') {
                            return scope.tags.selectedFacets[type] &&
                            scope.tags.selectedFacets[type].indexOf(desks.deskLookup[key].name) >= 0;
                        }

                        return scope.tags.selectedFacets[type] && scope.tags.selectedFacets[type].indexOf(key) >= 0;
                    };
                }
            };
        }])

        .directive('sdSearchTags', ['$location', '$route', 'tags', 'asset', 'metadata',
            function($location, $route, tags, asset, metadata) {
            return {
                scope: {},
                templateUrl: asset.templateUrl('superdesk-search/views/search-tags.html'),
                link: function(scope, elem) {

                    tags.initSelectedFacets().then(function(currentTags) {
                        scope.tags = currentTags;
                    });

                    scope.removeFilter = function(type, key) {
                        tags.removeFacet(type, key);
                    };

                    scope.removeParameter = function(param) {
                        var params = $location.search();
                        if (params.q) {
                            params.q = params.q.replace(param, '').trim();
                            $location.search('q', params.q || null);
                            // If it is subject code, remove it from left bar, too
                            if (param.indexOf('subject.name:') !== -1) {
                                var elementName = param.substring(
                                    param.lastIndexOf('(') + 1,
                                    param.lastIndexOf(')')
                                );

                                metadata.removeSubjectTerm(elementName);
                            }
                        }

                        if (param.indexOf('From Desk') >= 0) {
                            $location.search('from_desk', null);
                        }

                        if (param.indexOf('To Desk') >= 0) {
                            $location.search('to_desk', null);
                        }
                    };
                }
            };
        }])

        /**
         * Item list with sidebar preview
         */
        .directive('sdSearchResults', ['$location', 'preferencesService', 'packages', 'asset', '$timeout', 'api', 'search', 'session',
            function($location, preferencesService, packages, asset, $timeout, api, search, session) {
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

            var itemParameters = {
                compact: {
                    ITEM_HEIGHT: 57,
                    ITEMS_COUNT: 25,
                    BUFFER: 8
                },
                mgrid: {
                    ITEM_HEIGHT: 239,
                    ITEM_WIDTH: 190,
                    ITEMS_COUNT: 27,
                    ITEMS_ROW: 9,
                    BUFFER: 18
                }
            };

            return {
                require: '^sdSearchContainer',
                templateUrl: asset.templateUrl('superdesk-search/views/search-results.html'),
                link: function(scope, elem, attr, controller) {

                    var GRID_VIEW = 'mgrid',
                        LIST_VIEW = 'compact';

                    var multiSelectable = (attr.multiSelectable === undefined) ? false : true;

                    var updateTimeout,
                        criteria = search.query($location.search()).getCriteria(true),
                        list = elem[0].getElementsByClassName('list-view')[0],
                        scrollElem = elem.find('.content'),
                        oldQuery = _.omit($location.search(), '_id');

                    scope.flags = controller.flags;
                    scope.selected = scope.selected || {};

                    scope.repo = {
                        ingest: true, archive: true,
                        published: true, archived: true
                    };

                    scope.context = 'search';
                    scope.$on('item:deleted:archived', itemDelete);
                    scope.$on('item:published:no_post_publish_actions', itemDelete);
                    scope.$on('item:spike', queryItems);
                    scope.$on('item:unspike', queryItems);
                    scope.$on('item:duplicate', queryItems);

                    scrollElem.on('scroll', handleScroll);

                    scope.$watch('view', function(newValue, oldValue) {
                        if (newValue !== oldValue) {
                            scrollElem.scrollTop(0);
                            render();
                        }
                    });
                    scope.$watch(function getSearchParams() {
                        return _.omit($location.search(), '_id');
                    }, function(newValue, oldValue) {
                        if (newValue !== oldValue) {
                            queryItems().then(function () {
                                scrollElem.scrollTop(0);
                            });
                        }
                    }, true);

                    /*
                     * Function for creating small delay,
                     * before activating render function
                     */
                    function handleScroll() {
                        $timeout.cancel(updateTimeout);
                        updateTimeout = $timeout(render, 100, false);
                    }

                    /*
                     * Function for fetching total items and filling scope for the first time.
                     */
                    function queryItems() {
                        criteria = search.query($location.search()).getCriteria(true);
                        criteria.source.size = 0;
                        scope.total = null;
                        scope.preview(null);
                        return api.query(getProvider(criteria), criteria).then(function (items) {
                            scope.total = items._meta.total;
                            scope.$applyAsync(render);
                        });
                    }

                    /*
                     * Function to get the search endpoint name based on the criteria
                     *
                     * @param {Object} criteria
                     * @returns {string}
                     */
                    function getProvider(criteria) {
                        var provider = 'search';
                        if (criteria.repo && criteria.repo.indexOf(',') === -1) {
                            provider = criteria.repo;
                        }
                        if (scope.repo.search && scope.repo.search !== 'local') {
                            provider = scope.repo.search;
                        }
                        return provider;
                    }

                    /*
                     * Function for fetching the elements from the database
                     *
                     * @returns {undefined}
                     */
                    function render() {
                        var query = _.omit($location.search(), '_id');
                        var parameters = sourceParam();

                        if (!_.isEqual(_.omit(query, 'page'), _.omit(oldQuery, 'page'))) {
                            $location.search('page', null);
                        }

                        criteria = search.query($location.search()).getCriteria(true);
                        var tempItems;

                        criteria.source.from = parameters.from;
                        criteria.source.size = parameters.to - parameters.from;

                        api.query(getProvider(criteria), criteria).then(function (items) {
                            scope.$applyAsync(function () {
                                list.style.paddingTop = parameters.padding;
                                if (!scope.items) {
                                    scope.items = items;
                                } else {
                                    tempItems = {'_items': merge(items._items)};
                                    scope.items = _.assign(tempItems, _.omit(items, '_items'));
                                }
                            });
                        });

                        oldQuery = query;
                    }

                    /*
                     * Function for calculating number of fetched items
                     *
                     * @returns {Object} Returns object with criteria values
                     */
                    function sourceParam() {
                        var top, start, from, itemsCount, to, padding;

                        if (scope.view === 'mgrid') {
                            itemParameters[scope.view].ITEMS_ROW = Math.floor(scrollElem.width() / itemParameters[scope.view].ITEM_WIDTH);
                            itemParameters[scope.view].BUFFER = itemParameters[scope.view].ITEMS_ROW * 3;
                        }

                        top = scrollElem[0].scrollTop;
                        start = scope.view === 'mgrid' ?
                                Math.floor(top / itemParameters[scope.view].ITEM_HEIGHT) * itemParameters[scope.view].ITEMS_ROW :
                                Math.floor(top / itemParameters[scope.view].ITEM_HEIGHT);
                        from = Math.max(0, start - itemParameters[scope.view].BUFFER);
                        itemsCount = itemParameters[scope.view].ITEMS_COUNT;
                        to = Math.min(scope.total, start + itemsCount + itemParameters[scope.view].BUFFER);
                        padding = scope.view === 'mgrid' ?
                                (from * itemParameters[scope.view].ITEM_HEIGHT) / itemParameters[scope.view].ITEMS_ROW + 'px' :
                                (from * itemParameters[scope.view].ITEM_HEIGHT) + 'px';

                        return {from: from, to: to, padding: padding};
                    }

                    /*
                     * Function for filtering and merging new and old items
                     *
                     * @param {type} newItems New items fetched from the database
                     * @returns {Array} Filtered array with old and new data together
                     */
                    function merge(newItems) {
                        var next = [],
                            olditems = scope.items._items || [];

                        angular.forEach(newItems, function (item) {
                            var predicate = (item.state === 'ingested') ? {_id: item._id} :
                                {_id: item._id, _current_version: item._current_version};

                            var old = _.find(olditems, predicate);
                            next.push(old ? angular.extend(old, item) : item);
                        });

                        return next;
                    }

                    /*
                     * Function for updating list
                     * after item has been deleted
                     */
                    function itemDelete(e, data) {
                        if (session.identity._id === data.user) {
                            queryItems();
                        }
                    }

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

                    queryItems();

                    scope.openLightbox = function openLightbox() {
                        scope.selected.view = scope.selected.preview;
                    };

                    scope.closeLightbox = function closeLightbox() {
                        scope.selected.view = null;
                    };

                    scope.openSingleItem = function (packageItem) {
                        packages.fetchItem(packageItem).then(function(item) {
                            scope.selected.view = item;
                        });
                    };

                    scope.setview = setView;

                    var savedView;
                    preferencesService.get('archive:view').then(function(result) {
                        savedView = result.view;
                        scope.view = (!!savedView && savedView !== 'undefined') ? savedView : 'mgrid';
                    });

                    scope.$on('key:v', toggleView);

                    function setView(view) {
                        scope.view = view || 'mgrid';
                        update['archive:view'].view = view || 'mgrid';
                        preferencesService.update(update, 'archive:view');
                    }

                    function toggleView() {
                        var nextView = scope.view === LIST_VIEW ? GRID_VIEW : LIST_VIEW;
                        return setView(nextView);
                    }

                    /**
                     * Generates Identifier to be used by track by expression.
                     */
                    scope.generateTrackIdentifier = function(item) {
                        return (item.state === 'ingested') ? item._id : item._id + ':' + item._current_version;
                    };
                }
            };
        }])

        .directive('sdSearchWithin', ['$location', 'asset', function($location, asset) {
            return {
                scope: {},
                templateUrl: asset.templateUrl('superdesk-search/views/search-within.html'),
                link: function(scope, elem) {
                    scope.searchWithin = function() {
                        if (scope.within) {
                            var params = $location.search();
                            if (params.q) {
                                scope.query = params.q + ' (' + scope.within + ') ';
                            } else {
                                scope.query = '(' + scope.within + ')';
                            }
                            $location.search('q', scope.query || null);
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
                                if (desks.deskLookup[scope.item.task.desk]) {
                                    scope.item.container = 'desk:' + desks.deskLookup[scope.item.task.desk].name ;
                                }
                            });
                        } else {
                            if (scope.item._type === 'archive') {
                                scope.item.container = 'location:workspace';
                            } else {
                                if (scope.item._type === 'published' && scope.item.allow_post_publish_actions === false) {
                                    scope.item.container = 'archived';
                                }
                            }
                        }
                    }
                }
            };
        }])

        .directive('sdItemPreview', ['asset', function(asset) {
            return {
                templateUrl: asset.templateUrl('superdesk-search/views/item-preview.html'),
                scope: {
                    item: '=',
                    close: '&',
                    openLightbox: '=',
                    openSingleItem: '=',
                    hideActionsMenu: '='
                },
                link: function(scope) {
                    scope.tab = 'content';

                    scope.$watch('item', function(item) {
                        scope.selected = {preview: item || null};
                    });

                    scope.$on('item:spike', scope.close);

                    scope.$on('item:unspike', scope.close);

                    /**
                     * Return true if the menu actions from
                     * preview should be hidden
                     *
                     * @return {boolean}
                     */
                    scope.hideActions = function () {
                        return scope.hideActionsMenu;
                    };
                }
            };
        }])

        /**
         * Open Item dialog
         */
        .directive('sdItemGlobalsearch', ['superdesk', 'session', '$location', 'search', 'api', 'notify',
            'gettext', 'keyboardManager', 'asset', 'authoringWorkspace',
            function(superdesk, session, $location, search, api, notify, gettext, keyboardManager, asset, authoringWorkspace) {
            return {
                scope: {repo: '=', context: '='},
                templateUrl: asset.templateUrl('superdesk-search/views/item-globalsearch.html'),
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
                            authoringWorkspace.edit(items[0]);
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
                            repo: 'archive',
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
        .directive('sdItemSearchbar', ['$location', '$document', 'asset', function($location, $document, asset) {
            return {
                templateUrl: asset.templateUrl('superdesk-search/views/item-searchbar.html'),
                link: function(scope, elem) {
                    var ENTER = 13;

                    scope.focused = false;
                    var input = elem.find('#search-input');

                    scope.searchOnEnter = function($event) {
                        if ($event.keyCode === ENTER) {
                            scope.search();
                            $event.stopPropagation();
                        }
                    };

                    scope.search = function() {
                        $location.search('q', scope.query || null);
                    };

                    scope.cancel = function() {
                        scope.query = null;
                        scope.search();
                        input.focus();
                        //to be implemented
                    };

                    //initial query
                    var srch = $location.search();
                    if (srch.q && srch.q !== '') {
                        scope.query = srch.q;
                    } else {
                        scope.query = null;
                    }

                    function closeOnClick() {
                        scope.$apply(function() {
                            scope.focused = false;
                        });
                    }

                    $document.bind('click', closeOnClick);

                    scope.$on('$destroy', function() {
                        $document.unbind('click', closeOnClick);
                    });

                }
            };
        }])

        .directive('sdItemSearch', ['$location', '$timeout', 'asset', 'api', 'tags', 'search', 'metadata', 'desks',
            function($location, $timeout, asset, api, tags, search, metadata, desks) {
            return {
                scope: {
                    repo: '=',
                    context: '='
                },
                templateUrl: asset.templateUrl('superdesk-search/views/item-search.html'),
                link: function(scope, elem) {

                    var input = elem.find('#search-input');

                    function init() {
                        var params = $location.search();
                        scope.query = params.q;
                        scope.flags = false;
                        scope.desks = [];
                        scope.selectedDesk = {
                            from: null, to: null
                        };

                        fetchProviders();

                        if (params.repo) {
                            var param_list = params.repo.split(',');
                            scope.repo.archive = param_list.indexOf('archive') >= 0;
                            scope.repo.ingest = param_list.indexOf('ingest') >= 0;
                            scope.repo.published = param_list.indexOf('published') >= 0;
                            scope.repo.archived = param_list.indexOf('archived') >= 0;
                        }

                        if (!scope.repo) {
                            scope.repo = {'search': 'local'};
                        } else {
                            if (!scope.repo.archive && !scope.repo.ingest && !scope.repo.published && !scope.repo.archived) {
                                scope.repo.search = params.repo;
                            } else {
                                scope.repo.search = 'local';
                            }
                        }

                        desks.initialize()
                            .then(function() {
                                scope.desks = desks.desks;
                                initFromToDesk($location.search().from_desk, 'from');
                                initFromToDesk($location.search().to_desk, 'to');
                            });
                    }

                    init();

                    function fetchProviders() {
                        return api.ingestProviders.query({max_results: 200})
                            .then(function(result) {
                                scope.providers = result._items;
                            });
                    }

                    /*
                     * initialize the desk drop down selection.
                     * @param {string} query string parameter from_desk or to_desk
                     * @param {field} scope field to be updated.
                     */
                    function initFromToDesk(param, field) {
                        if (param) {
                            var deskParams = param.split('-');
                            if (deskParams.length === 2) {
                                scope.selectedDesk[field] = deskParams[0];
                            }
                        }
                    }

                    scope.$on('$locationChangeSuccess', function() {
                        if (scope.query !== $location.search().q ||
                            scope.selectedDesk.from !== $location.search().from_desk ||
                            scope.selectedDesk.to !== $location.search().to_desk) {
                            init();
                        }
                    });

                    function getActiveRepos() {
                        var repos = [];

                        if (scope.repo.search === 'local') {
                            angular.forEach(scope.repo, function(val, key) {
                                if (val && val !== 'local') {
                                    repos.push(key);
                                }
                            });

                            return repos.length ? repos.join(',') : null;

                        } else {
                            return scope.repo.search;
                        }
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

                        if (metas.length) {
                            if (scope.query) {
                                return scope.query + ' ' + metas.join(' ');
                            } else {
                                return metas.join(' ');
                            }
                        } else {
                            return scope.query || null;
                        }

                    }

                    /**
                     * Function which dictates whether the Go button should be enabled or disabled.
                     *
                     * @return {boolean} true if Go button in parameters section should be enabled. false otherwise.
                     */
                    scope.isSearchEnabled = function() {
                        return scope.repo.search && (scope.repo.search !== 'local' ||
                            (scope.repo.ingest || scope.repo.archive || scope.repo.published || scope.repo.archived));
                    };

                    scope.focusOnSearch = function() {
                        if (scope.advancedOpen) {
                            scope.toggle();
                        }
                        input.focus();
                    };

                    function updateParam() {
                        scope.query = $location.search().q;
                        $location.search('q', getQuery() || null);
                        $location.search('repo', getActiveRepos());
                        scope.meta = {};
                    }

                    scope.search = function() {
                        updateParam();
                    };

                    scope.$on('key:s', function openSearch() {
                        scope.$apply(function() {
                            scope.flags = {extended: true};
                            $timeout(function() { // call focus when input will be visible
                                input.focus();
                            }, 0, false);
                        });
                    });

                    /*
                     * Converting to object and adding pre-selected subject codes to list in left sidebar
                     */
                    metadata
                        .fetchSubjectcodes()
                        .then(function () {
                            scope.subjectcodes = metadata.values.subjectcodes;
                            return tags.initSelectedFacets();
                        })
                        .then(function (currentTags) {
                            scope.subjectitems = {
                                subject: search.getSubjectCodes(currentTags, scope.subjectcodes)
                            };
                        });

                    /*
                     * filter content by desk.
                     */
                    scope.deskSearch = function () {
                        $location.search('from_desk', getDeskParam('from'));
                        $location.search('to_desk', getDeskParam('to'));
                    };

                    /*
                     * Get the Desk Type
                     * @param {string} field from or to
                     * @returns {string} desk querystring parameter
                     */
                    function getDeskParam(field) {
                        var deskId = '';
                        if (scope.selectedDesk[field]) {
                            deskId = scope.selectedDesk[field];
                            var desk_type = _.result(_.find(scope.desks._items, function (item) {
                                return item._id === deskId;
                            }), 'desk_type');

                            return deskId + '-' + desk_type;
                        }

                        return null;
                    }

                    /*
                     * Filter content by subject search
                     */
                    scope.subjectSearch = function (item) {
                        tags.initSelectedFacets().then(function (currentTags) {
                            var subjectCodes = search.getSubjectCodes(currentTags, scope.subjectcodes);
                            if (item.subject.length > subjectCodes.length) {
                                /* Adding subject codes to filter */
                                var addItemSubjectName = 'subject.name:(' + item.subject[item.subject.length - 1].name + ')',
                                    q = (scope.query ? scope.query + ' ' + addItemSubjectName : addItemSubjectName);

                                $location.search('q', q);
                            } else {
                                /* Removing subject codes from filter */
                                var params = $location.search();
                                if (params.q) {
                                    for (var j = 0; j < subjectCodes.length; j++) {
                                        if (item.subject.indexOf(subjectCodes[j]) === -1) {
                                            var removeItemSubjectName = 'subject.name:(' + subjectCodes[j].name + ')';
                                            params.q = params.q.replace(removeItemSubjectName, '').trim();
                                            $location.search('q', params.q || null);
                                        }
                                    }
                                }
                            }
                        });
                    };
                }
            };
        }])

        /**
         * Item sort component
         */
        .directive('sdItemSortbar', ['search', 'asset', '$location', function sortBarDirective(search, asset, $location) {
            return {
                scope: {},
                templateUrl: asset.templateUrl('superdesk-search/views/item-sortbar.html'),
                link: function(scope) {
                    scope.sortOptions = search.sortOptions;

                    function getActive() {
                        scope.active = search.getSort();
                    }

                    scope.canSort = function() {
                        var criteria = search.query($location.search()).getCriteria(true);
                        return !(angular.isDefined(criteria.repo) && criteria.repo === 'aapmm');
                    };

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

        .directive('sdSavedSearchSelect', ['api', 'session', function SavedSearchSelectDirective(api, session) {
            return {
                link: function(scope) {
                    api.query('saved_searches', {}, session.identity).then(function(res) {
                        scope.searches = res._items;
                    });
                }
            };
        }])

        .directive('sdSavedSearches', ['api', 'session', '$location', 'notify', 'gettext', 'asset',
        function(api, session, $location, notify, gettext, asset) {
            return {
                templateUrl: asset.templateUrl('superdesk-search/views/saved-searches.html'),
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

        .directive('sdMultiActionBar', ['asset', 'multi', 'authoringWorkspace',
        function(asset, multi, authoringWorkspace) {
            return {
                controller: 'MultiActionBar',
                controllerAs: 'action',
                templateUrl: asset.templateUrl('superdesk-search/views/multi-action-bar.html'),
                scope: true,
                link: function(scope) {
                    scope.multi = multi;
                    scope.$watch(multi.getItems, detectType);

                    scope.isOpenItemType = function(type) {
                        var openItem = authoringWorkspace.getItem();
                        return openItem.type === type;
                    };

                    /**
                     * Detects type of all selected items and assign it to scope,
                     * but only when it's same for all of them.
                     *
                     * @param {Array} items
                     */
                    function detectType(items) {
                        var types = {};
                        var states = [];
                        angular.forEach(items, function(item) {
                            types[item._type] = 1;
                            states.push(item.state);
                        });

                        var typesList = Object.keys(types);
                        scope.type = typesList.length === 1 ? typesList[0] : null;
                        scope.state = typesList.length === 1 ? states[0] : null;
                    }
                }
            };
        }])

        .config(['superdeskProvider', 'assetProvider', function(superdesk, asset) {
            superdesk.activity('/search', {
                description: gettext('Find live and archived content'),
                priority: 200,
                label: gettext('Search'),
                templateUrl: asset.templateUrl('superdesk-search/views/search.html'),
                sideTemplateUrl: 'scripts/superdesk-workspace/views/workspace-sidenav.html'
            });
        }]);

    MultiActionBarController.$inject = ['$rootScope', 'multi', 'multiEdit', 'send',
                                        'packages', 'superdesk', 'notify', 'spike', 'authoring'];
    function MultiActionBarController($rootScope, multi, multiEdit, send, packages, superdesk, notify, spike, authoring) {
        this.send  = function() {
            return send.all(multi.getItems());
        };

        this.sendAs = function() {
            return send.allAs(multi.getItems());
        };

        this.multiedit = function() {
            multiEdit.create(multi.getIds());
            multiEdit.open();
        };

        this.createPackage = function() {
            packages.createPackageFromItems(multi.getItems())
            .then(function(new_package) {
                superdesk.intent('edit', 'item', new_package);
            }, function(response) {
                if (response.status === 403 && response.data && response.data._message) {
                    notify.error(gettext(response.data._message), 3000);
                }
            });
        };

        this.addToPackage = function() {
            $rootScope.$broadcast('package:addItems', {items: multi.getItems(), group: 'main'});
        };

        /**
         * Multiple item spike
         */
        this.spikeItems = function() {
            spike.spikeMultiple(multi.getItems());
            $rootScope.$broadcast('item:spike');
            multi.reset();
        };

        /**
         * Multiple item unspike
         */
        this.unspikeItems = function() {
            spike.unspikeMultiple(multi.getItems());
            $rootScope.$broadcast('item:unspike');
            multi.reset();
        };

        this.canSpikeItems = function() {
            var canSpike = true;
            multi.getItems().forEach(function(item) {
                canSpike = canSpike && authoring.itemActions(item).spike;
            });
            return canSpike;
        };
    }
})();
