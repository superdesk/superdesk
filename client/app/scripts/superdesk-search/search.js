(function() {
    'use strict';

    var PARAMETERS = Object.freeze({
        unique_name: 'Unique Name',
        original_creator: 'Creator',
        from_desk: 'From Desk',
        to_desk: 'To Desk'
    });

    SearchService.$inject = ['$location', 'gettext'];
    function SearchService($location, gettext) {
        var sortOptions = [
            {field: 'versioncreated', label: gettext('Updated')},
            {field: 'firstcreated', label: gettext('Created')},
            {field: 'urgency', label: gettext('News Value')},
            {field: 'anpa_category.name', label: gettext('Category')},
            {field: 'slugline.phrase', label: gettext('Slugline')},
            {field: 'priority', label: gettext('Priority')},
            {field: 'genre.name', label: gettext('Genre')}
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
         * Set filters for parameters
         */
        function setParameters(filters, params) {
            _.each(PARAMETERS, function(value, key) {
                if (params[key]) {
                    var desk;
                    switch (key) {
                        case 'from_desk':
                            desk = params[key].split('-');
                            if (desk.length === 2) {
                                if (desk[1] === 'authoring') {
                                    filters.push({'term': {'task.last_authoring_desk': desk[0]}});
                                } else {
                                    filters.push({'term': {'task.last_production_desk': desk[0]}});
                                }
                            }
                            break;
                        case 'to_desk':
                            desk = params[key].split('-');
                            if (desk.length === 2) {
                                filters.push({'term': {'task.desk': desk[0]}});
                                if (!params.from_desk) {
                                    var field = desk[1] === 'authoring' ? 'task.last_production_desk' : 'task.last_authoring_desk';
                                    filters.push({'exists': {'field': field}});
                                }
                            }
                            break;
                        default:
                            var filter = {'term': {}};
                            filter.term[key] = params[key];
                            filters.push(filter);
                    }
                }
            });
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
                if (queryArrayElement.indexOf('subject.qcode') !== -1 ||
                    queryArrayElement.indexOf('subject.name') !== -1) {
                    var elementName = queryArrayElement.substring(
                            queryArrayElement.lastIndexOf('(') + 1,
                            queryArrayElement.lastIndexOf(')'));
                    for (var j = 0, subjectCodesLength = subjectcodes.length; j < subjectCodesLength; j++) {
                        if (subjectcodes[j].qcode === elementName || subjectcodes[j].name === elementName) {
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

                if (params.genre) {
                    query.post_filter({terms: {'genre.name': JSON.parse(params.genre)}});
                }

                if (params.desk) {
                    query.post_filter({terms: {'task.desk': JSON.parse(params.desk)}});
                }

                if (params.stage) {
                    query.post_filter({terms: {'task.stage': JSON.parse(params.stage)}});
                }

                if (params.legal) {
                    query.post_filter({terms: {'flags.marked_for_legal': JSON.parse(params.legal)}});
                }
            }

            /**
             * Get criteria for given query
             */
            this.getCriteria = function getCriteria(withSource) {
                var search = params;
                var sort = getSort();
                setParameters(filters, params);
                var criteria = {
                    query: {filtered: {filter: {and: filters}}},
                    sort: [_.zipObject([sort.field], [sort.dir])]
                };

                if (post_filters.length > 0) {
                    criteria.post_filter = {'and': post_filters};
                }

                if (search.q) {
                    criteria.query.filtered.query = {query_string: {
                        query: search.q.replace(/\//g, '\\/'),
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

        /*
         * Generate Track By Identifier for search results.
         */
        this.generateTrackByIdentifier = function (item) {
            return (item.state === 'ingested') ? item._id : item._id + ':' + item._current_version;
        };
    }

    TagService.$inject = ['$location', 'desks', 'userList', 'metadata'];
    function TagService($location, desks, userList, metadata) {
        var tags = {};
        tags.selectedFacets = {};
        tags.selectedParameters = [];
        tags.selectedKeywords = [];
        tags.currentSearch = {};

        var subjects;

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
            'stage': 1,
            'genre': 1,
            'legal': 1
        };

        metadata
            .fetchSubjectcodes()
            .then(function () {
                subjects = metadata.values.subjectcodes;
            });

        function initSelectedParameters (parameters) {
            tags.selectedParameters = [];
            while (parameters.indexOf(':') > 0 &&
                   parameters.indexOf(':') < parameters.indexOf('(') &&
                   parameters.indexOf(':') < parameters.indexOf(')')) {

                var colonIndex = parameters.indexOf(':');
                var parameter = parameters.substring(parameters.lastIndexOf(' ', colonIndex), parameters.indexOf(')', colonIndex) + 1);

                if (parameter.indexOf('subject.qcode') !== -1) {
                    var value = parameter.substring(parameter.indexOf('(') + 1, parameter.lastIndexOf(')'));
                    var subjectName = _.result(_.find(subjects, {qcode: value}), 'name');

                    tags.selectedParameters.push('subject.name:(' + subjectName + ')');

                } else {
                    tags.selectedParameters.push(parameter);
                }

                parameters = parameters.replace(parameter, '');
            }

            return parameters;
        }

        function initSelectedKeywords (keywords) {
            tags.selectedKeywords = [];
            while (keywords.indexOf('(') >= 0 && keywords.indexOf(')') > 0) {
                var closeIndex = keywords.indexOf('(');
                var counter = 1;
                while (counter > 0 && closeIndex < keywords.length) {
                    var c = keywords[++closeIndex];
                    if (c === '(') {
                        counter++;
                    } else if (c === ')') {
                        counter--;
                    }
                }
                var keyword = keywords.substring(keywords.indexOf('('), closeIndex + 1);
                tags.selectedKeywords.push(keyword);
                keywords = keywords.replace(keyword, '');
            }
        }

        function initParameters(params) {
            _.each(PARAMETERS, function(value, key) {
                if (angular.isDefined(params[key])) {
                    switch (key) {
                        case 'original_creator':
                            userList.getUser(params[key]).then(function(user) {
                                tags.selectedParameters.push(value + ':' + user.display_name);
                            }, function(error) {
                                tags.selectedParameters.push(value + ':Unknown');
                            });
                            break;
                        case 'from_desk':
                        case 'to_desk':
                            tags.selectedParameters.push(value + ':' +
                                desks.deskLookup[params[key].split('-')[0]].name);
                            break;
                        default:
                            tags.selectedParameters.push(value + ':' + params[key]);
                    }
                }
            });
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

                initParameters(tags.currentSearch);

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
                    scope.editingSearch = false;
                    scope.showSaveSearch = false;

                    scope.aggregations = {};
                    scope.privileges = privileges.privileges;

                    scope.$on('edit:search', function(event, args)  {
                        scope.sTab = true;
                        scope.editingSearch = args;
                    });

                    scope.changeTab = function() {
                        scope.sTab = !scope.sTab;
                    };

                    scope.resetEditingSearch = function() {
                        scope.editingSearch = false;
                    };

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
                            'priority': {},
                            'genre': {},
                            'legal': {}
                        };
                    };

                    initAggregations();

                    scope.$watch('items', function() {
                        tags.initSelectedFacets().then(function(currentTags) {

                            scope.tags = currentTags;

                            if (!scope.items || scope.items._aggregations === undefined) {
                                return;
                            }

                            if (angular.isDefined(scope.items._aggregations.type)) {
                                _.forEach(scope.items._aggregations.type.buckets, function(type) {
                                    scope.aggregations.type[type.key] = type.doc_count;
                                });
                            }

                            if (angular.isDefined(scope.items._aggregations.category)) {
                                _.forEach(scope.items._aggregations.category.buckets, function(cat) {
                                    if (cat.key !== '') {
                                        scope.aggregations.category[cat.key] = cat.doc_count;
                                    }
                                });
                            }

                            if (angular.isDefined(scope.items._aggregations.genre)) {
                                _.forEach(scope.items._aggregations.genre.buckets, function(g) {
                                    if (g.key !== '') {
                                        scope.aggregations.genre[g.key] = g.doc_count;
                                    }
                                });
                            }

                            if (angular.isDefined(scope.items._aggregations.urgency))
                            {
                                _.forEach(scope.items._aggregations.urgency.buckets, function(urgency) {
                                    scope.aggregations.urgency[urgency.key] = urgency.doc_count;
                                });
                            }

                            if (angular.isDefined(scope.items._aggregations.priority)) {
                                _.forEach(scope.items._aggregations.priority.buckets, function(priority) {
                                    scope.aggregations.priority[priority.key] = priority.doc_count;
                                });
                            }

                            if (angular.isDefined(scope.items._aggregations.source)) {
                                _.forEach(scope.items._aggregations.source.buckets, function(source) {
                                    scope.aggregations.source[source.key] = source.doc_count;
                                });
                            }

                            if (angular.isDefined(scope.items._aggregations.credit)) {
                                _.forEach(scope.items._aggregations.credit.buckets, function(credit) {
                                    scope.aggregations.credit[credit.key] = {'count': credit.doc_count, 'qcode': credit.qcode};
                                });
                            }

                            if (angular.isDefined(scope.items._aggregations.day)) {
                                _.forEach(scope.items._aggregations.day.buckets, function(day) {
                                    scope.aggregations.date['Last Day'] = day.doc_count;
                                });
                            }

                            if (angular.isDefined(scope.items._aggregations.week)) {
                                _.forEach(scope.items._aggregations.week.buckets, function(week) {
                                    scope.aggregations.date['Last Week'] = week.doc_count;
                                });
                            }

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

                            if (angular.isDefined(scope.items._aggregations.legal)) {
                                _.forEach(scope.items._aggregations.legal.buckets, function(l) {
                                    if (l.key === 'T' && l.doc_count > 0) {
                                        scope.aggregations.legal = {count: l.doc_count};
                                    }
                                });
                            }

                        });
                    });

                    scope.$watch('tags.currentSearch', function(currentSearch) {
                        scope.showSaveSearch = _.isEmpty(currentSearch) ? false : true;
                    }, true);

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

                        return scope.tags && scope.tags.selectedFacets[type] && scope.tags.selectedFacets[type].indexOf(key) >= 0;
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

                    metadata
                        .fetchSubjectcodes()
                        .then(function () {
                            scope.subjectcodes = metadata.values.subjectcodes;
                        });

                    scope.removeParameter = function(param) {
                        var params = $location.search();
                        if (params.q) {
                            // If it is subject code, remove it from left bar, too
                            if (param.indexOf('subject.name:') !== -1) {
                                var elementName = param.substring(
                                    param.lastIndexOf('(') + 1,
                                    param.lastIndexOf(')')
                                );

                                var qcode = _.result(_.find(scope.subjectcodes, function(item) {
                                                        return item.name === elementName;
                                                    }), 'qcode');

                                params.q = params.q.replace('subject.qcode:(' + qcode + ')', '').trim();
                                $location.search('q', params.q || null);

                                metadata.removeSubjectTerm(elementName);
                            } else {
                                params.q = params.q.replace(param, '').trim();
                                $location.search('q', params.q || null);
                            }
                        }

                        _.each(PARAMETERS, function(val, key) {
                            if (param.indexOf(val) !== -1) {
                                $location.search(key, null);
                            }
                        });
                    };
                }
            };
        }])

        /**
         * Item list with sidebar preview
         */
        .directive('sdSearchResults', [
            '$location',
            'preferencesService',
            'packages',
            'asset',
            '$timeout',
            'api',
            'search',
            'session',
            'moment',
            'gettext',
            'superdesk',
            'workflowService',
            'archiveService',
            'activityService',
            'multi',
            'desks',
            'familyService',
        function(
            $location,
            preferencesService,
            packages,
            asset,
            $timeout,
            api,
            search,
            session,
            moment,
            gettext,
            superdesk,
            workflowService,
            archiveService,
            activityService,
            multi,
            desks,
            familyService
        ) { // uff - should it use injector instead?
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
                templateUrl: asset.templateUrl('superdesk-search/views/search-results.html'),
                link: function(scope, elem, attr, controller) {

                    var GRID_VIEW = 'mgrid',
                        LIST_VIEW = 'compact';

                    var multiSelectable = (attr.multiSelectable === undefined) ? false : true;

                    scope.previewingBroadcast = false;

                    var updateTimeout,
                        criteria = search.query($location.search()).getCriteria(true),
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
                    scope.$on('item:spike', queryItems);
                    scope.$on('item:unspike', queryItems);
                    scope.$on('item:duplicate', queryItems);
                    scope.$on('content:expired', queryItems);
                    scope.$on('broadcast:preview', function(event, args) {
                        scope.previewingBroadcast = true;
                        scope.preview(args.item);
                    });
                    scope.$on('broadcast:created', function(event, args) {
                        scope.previewingBroadcast = true;
                        queryItems();
                        scope.preview(args.item);
                    });

                    scrollElem.on('scroll', handleScroll);

                    scope.$watch('view', function(newValue, oldValue) {
                        if (newValue !== oldValue) {
                            console.time('view');
                            listComponent.setState({view: newValue}, function() {
                                console.timeEnd('view');
                            });
                        }
                    });

                    scope.$watch('selected', function(newVal, oldVal) {
                        if (!newVal && scope.previewingBroadcast) {
                            scope.previewingBroadcast = false;
                        }
                    });

                    scope.$watch(function getSearchParams() {
                        return _.omit($location.search(), '_id');
                    }, function(newValue, oldValue) {
                        if (newValue !== oldValue) {
                            queryItems();
                        }
                    }, true);

                    /*
                     * Function for creating small delay,
                     * before activating render function
                     */
                    function handleScroll($event) {
                        if (scope.rendering) {
                            $event.preventDefault();
                            return;
                        }

                        $timeout.cancel(updateTimeout);
                        updateTimeout = $timeout(renderIfNeeded, 100, false);
                    }

                    scope.rendering = false;
                    var list = document.getElementById('content-list');

                    /**
                     * Trigger render in case user scrolls to the very end of list
                     */
                    function renderIfNeeded() {
                        if (!scope.items) {
                            return; // automatic scroll after removing items
                        }

                        if (isListEnd(list) && !scope.rendering) {
                            scope.rendering = true;
                            render(null, true);
                        }
                    }

                    /**
                     * Check if we reached end of the list elem
                     *
                     * @param {Element} list
                     * @return {Boolean}
                     */
                    function isListEnd(list) {
                        return list.scrollTop + list.offsetHeight + 50 >= list.scrollHeight;
                    }

                    /*
                     * Function for fetching total items and filling scope for the first time.
                     */
                    function queryItems() {
                        criteria = search.query($location.search()).getCriteria(true);
                        criteria.source.size = 50;
                        criteria.source.from = 0;
                        scope.total = null;
                        scope.items = null;
                        if (!scope.previewingBroadcast) {
                            scope.preview(null);
                        }
                        return api.query(getProvider(criteria), criteria).then(function (items) {
                            scope.total = items._meta.total;
                            scope.$applyAsync(function() {
                                render(items);
                            });
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
                     * @param {items}
                     */
                    function render(items, next) {
                        if (items) {
                            setScopeItems(items);
                        } else if (next) {
                            criteria.source.from = (criteria.source.from || 0) + criteria.source.size;
                            api.query(getProvider(criteria), criteria).then(setScopeItems);
                        } else {
                            var query = _.omit($location.search(), '_id');

                            if (!_.isEqual(_.omit(query, 'page'), _.omit(oldQuery, 'page'))) {
                                $location.search('page', null);
                            }

                            criteria = search.query($location.search()).getCriteria(true);
                            criteria.source.from = 0;
                            criteria.source.size = 50;
                            api.query(getProvider(criteria), criteria).then(setScopeItems);
                            oldQuery = query;
                        }

                        function setScopeItems(items) {
                            if (!scope.items) { // initial set of items
                                scope.itemsById = {};
                                scope.itemsList = [];
                                items._items.forEach(function(item) {
                                    scope.itemsById[item._id] = item;
                                    scope.itemsList.push(item._id);
                                });
                            } else if (next) { // adding new items to list
                                items._items.forEach(function(item) {
                                    if (!scope.itemsById[item._id]) {
                                        scope.itemsById[item._id] = item;
                                        scope.itemsList.push(item._id);
                                    } else if (scope.itemsById[item._id]._etag !== item._etag) {
                                        scope.itemsById[item._id] = item;
                                    }
                                });
                            } else { // replacing items with new ones, but keep old objects if not changed
                                var oldItems = scope.itemsById;
                                scope.itemsList = [];
                                scope.itemsById = {};
                                items._items.forEach(function(item) {
                                    scope.itemsList.push(item._id);
                                    if (oldItems[item._id] && oldItems[item._id]._etag === item._etag) {
                                        scope.itemsById = oldItems[item._id];
                                    } else {
                                        scope.itemsById = item;
                                    }
                                });
                            }

                            // set for aggregations
                            scope.items = items;

                            console.time('render');
                            listComponent.setState({
                                view: scope.view,
                                itemsList: scope.itemsList,
                                itemsById: scope.itemsById
                            });
                            console.timeEnd('render');
                            console.log('items:', scope.itemsList.length);
                            scope.rendering = false;
                        }
                    }

                    scope.itemsList = [];
                    scope.itemsById = {};

                    /**
                     * Test if an item has thumbnail
                     *
                     * @return {Boolean}
                     */
                    function hasThumbnail(item) {
                        return item.type === 'picture' && item.renditions.thumbnail;
                    }

                    /**
                     * Media Preview - renders item thumbnail
                     */
                    var MediaPreview = function(props) {
                        var item = props.item;
                        var headline = item.headline || item.slugline || item.type;
                        var preview;

                        if (hasThumbnail(props.item)) {
                            preview = React.createElement(
                                'img',
                                {src: props.item.renditions.thumbnail.href}
                            );
                        }

                        return React.createElement(
                            'div',
                            {className: 'media multi'},
                            preview ? React.createElement(
                                'figure',
                                null,
                                preview
                            ) : null,
                            React.createElement(
                                'span',
                                {className: 'text'},
                                React.createElement(
                                    'small',
                                    {title: headline},
                                    headline.substr(0, 90)
                                ),
                                React.createElement(ItemContainer, {item: item, desk: props.desk})
                            ),
                            React.createElement(SelectBox, {item: item, onMultiSelect: props.onMultiSelect})
                        );
                    };

                    var SelectBox = React.createClass({
                        toggle: function(event) {
                            event.stopPropagation();
                            var selected = !this.props.item.selected;
                            this.props.onMultiSelect(this.props.item, selected);
                        },

                        render: function() {
                            return React.createElement(
                                'div',
                                {className: 'selectbox', onClick: this.toggle},
                                React.createElement(
                                    'span',
                                    {className: 'sd-checkbox' + (this.props.item.selected ? ' checked' : '')}
                                )
                            );
                        }
                    });

                    var ItemContainer = function(props) {
                        var item = props.item;
                        var desk = props.desk || null;
                        var label, value;

                        if (item._type !== 'ingest') {
                            if (desk) {
                                label = gettext('desk:');
                                value = desk.name;
                            } else {
                                if (item._type === 'archive') {
                                    label = gettext('location:');
                                    value = gettext('workspace');
                                } else {
                                    if (item._type === 'published' && item.allow_post_publish_actions === false) {
                                        label = '';
                                        value = gettext('archived');
                                    }
                                }
                            }
                        }

                        return React.createElement(
                            'span',
                            {className: 'container', title: value ? label + ' ' + value : null},
                            React.createElement(
                                'span',
                                {className: 'location-desk-label'},
                                label
                            ),
                            value
                        );
                    };

                    /**
                     * Media Info - renders item metadata
                     */
                    var MediaInfo = function(props) {
                        var item = props.item;
                        var meta = [];

                        if (props.ingestProvider) {
                            meta.push(
                                React.createElement('dt', {key: 1}, gettext('source')),
                                React.createElement('dd', {key: 2, className: 'provider'}, props.ingestProvider.name)
                            );
                        }

                        meta.push(
                            React.createElement('dt', {key: 3}, gettext('updated')),
                            React.createElement('dd', {key: 4}, moment(item.versioncreated).fromNow())
                        );

                        if (item.is_spiked) {
                            meta.push(React.createElement('dt', {key: 5}, gettext('expires')));
                            meta.push(React.createElement('dd', {key: 6}, moment(item.expiry).fromNow()));
                        }

                        var info = [];
                        var flags = item.flags || {};

                        info.push(React.createElement(
                            'h5',
                            {key: 1},
                            item.slugline || item.type
                        ));

                        info.push(React.createElement(
                            'dl',
                            {key: 2},
                            meta
                        ));

                        if (flags.marked_for_not_publication) {
                            info.push(React.createElement(
                                'div',
                                {key: 3, className: 'state-label not-for-publication'},
                                gettext('Not for publication')
                            ));
                        }

                        if (flags.marked_for_legal) {
                            info.push(React.createElement(
                                'div',
                                {key: 4, className: 'state-label legal'},
                                gettext('Legal')
                            ));
                        }

                        if (item.archived) {
                            info.push(React.createElement(
                                'div',
                                {className: 'fetched-desk', key: 5},
                                React.createElement(FetchedDesksInfo, {item: item})
                            ));
                        }

                        return React.createElement('div', {className: 'media-info'}, info);
                    };

                    /**
                     * Type icon component
                     */
                    var TypeIcon = function(props) {
                        return React.createElement('i', {className: 'filetype-icon-' + props.type});
                    };

                    var GridTypeIcon = function(props) {
                        return React.createElement(
                            'span',
                            {className: 'type-icon'},
                            React.createElement(TypeIcon, {type: props.item.type})
                        );
                    };

                    var ListTypeIcon = React.createClass({
                        getInitialState: function() {
                            return {hover: false};
                        },

                        setHover: function() {
                            this.setState({hover: true});
                        },

                        unsetHover: function() {
                            this.setState({hover: false});
                        },

                        render: function() {
                            var showSelect = this.state.hover || this.props.item.selected;
                            return React.createElement(
                                'div',
                                {className: 'list-field type-icon', onMouseEnter: this.setHover, onMouseLeave: this.unsetHover},
                                showSelect ?
                                    React.createElement(SelectBox, {item: this.props.item, onMultiSelect: this.props.onMultiSelect}) :
                                    React.createElement(TypeIcon, {type: this.props.item.type})
                            );
                        }
                    });

                    var ItemPriority = function(props) {
                        var priority = props.priority || 3;
                        return React.createElement(
                            'span',
                            {className: 'priority-label priority-label--' + priority},
                            priority
                        );
                    };

                    var ListPriority = function(props) {
                        var item = props.item;
                        return React.createElement(
                            'div',
                            {className: 'list-field urgency'},
                            item.priority ?
                                React.createElement(
                                    'span',
                                    {className: 'priority-label priority-label--' + item.priority},
                                    item.priority
                                ) :
                                React.createElement(
                                    'span',
                                    {className: 'output-item-label label-' + item.urgency},
                                    item.urgency
                                )
                        );
                    };

                    var HighlightsInfo = React.createClass({
                        render: function() {
                            var highlights = this.props.item.highlights || [];
                            return React.createElement(
                                'div',
                                {className: 'highlights-box'},
                                highlights.length ?
                                    React.createElement(
                                        'div',
                                        {className: 'highlights-list dropdown'},
                                        React.createElement(
                                            'button',
                                            {className: 'dropdown-toggle'},
                                            React.createElement('i', {
                                                className: classNames({
                                                    'icon-star red': highlights.length === 1,
                                                    'icon-multi-star red': highlights.length > 1
                                                })
                                            })
                                        )

                                    ) : null
                            );
                        }
                    });

                    var DesksDropdown = React.createClass({
                        getInitialState: function() {
                            return {open: false};
                        },

                        toggle: function(event) {
                            event.stopPropagation();
                            this.setState({open: !this.state.open});
                        },

                        render: function() {
                            var desks = this.props.desks.map(function(desk, index) {
                                return React.createElement(
                                    'li',
                                    {key: 'desk' + index},
                                    React.createElement(
                                        'a',
                                        {disabled: !desk.isUserDeskMember, onClick: this.props.openDesk(desk)},
                                        desk.desk.name + ' (' + desk.count + ')'
                                    )
                                );
                            }.bind(this));

                            return React.createElement(
                                'dd',
                                {className: 'dropdown dropup more-actions'},
                                React.createElement(
                                    'button',
                                    {className: 'dropdown-toggle', onClick: this.toggle},
                                    React.createElement('i', {className: 'icon-dots'})
                                ),
                                React.createElement(
                                    'div',
                                    {className: 'dropdown-menu'},
                                    React.createElement('ul', {}, desks)
                                )
                            );
                        }
                    });

                    var FetchedDesksInfo = React.createClass({
                        getInitialState: function() {
                            return {desks: []};
                        },

                        componentDidMount: function() {
                            familyService.fetchDesks(this.props.item, false)
                                .then(function(fetchedDesks) {
                                    this.setState({desks: fetchedDesks});
                                }.bind(this));
                        },

                        formatDeskName: function(name) {
                            return name.substr(0, 10) + (name.length > 10 ? '...' : '');
                        },

                        openDesk: function(desk) {
                            return function(event) {
                                event.stopPropagation();
                                if (desk.isUserDeskMember) {
                                    desks.setCurrentDeskId(desk.desk._id);
                                    $location.url('/workspace/monitoring');
                                    if (desk.count === 1) {
                                        superdesk.intent('edit', 'item', desk.item);
                                    }
                                }
                            };
                        },

                        render: function() {
                            var items = [];
                            items.push(React.createElement('dt', {key: 'dt'}, gettext('fetched in')));

                            if (this.state.desks.length) {
                                var desk = this.state.desks[0];
                                var name = this.formatDeskName(desk.desk.name);
                                items.push(React.createElement('dd', {key: 'dd1'}, desk.isUserDeskMember ?
                                    React.createElement('a', {onClick: this.openDesk(desk)}, name) :
                                    React.createElement('span', {className: 'container'}, name)
                                ));

                                if (this.state.desks.length > 1) {
                                    items.push(React.createElement(DesksDropdown, {
                                        key: 'dd2',
                                        desks: this.state.desks,
                                        openDesk: this.openDesk
                                    }));
                                }
                            }

                            return React.createElement('div', {},
                                React.createElement(
                                    'dl',
                                    {},
                                    items
                                )
                            );
                        }
                    });

                    var ListItemInfo = function(props) {
                        var item = props.item;
                        var flags = item.flags || {};
                        var anpa = item.anpa_category || {};
                        var broadcast = item.broadcast || {};
                        var provider = props.ingestProvider || {name: null};
                        return React.createElement(
                            'div',
                            {className: 'item-info'},
                            React.createElement('div', {className: 'line'},
                                React.createElement('span', {className: 'word-count'}, item.word_count),
                                item.slugline ? React.createElement('span', {className: 'keyword'}, item.slugline.substr(0, 40)) : null,
                                React.createElement(HighlightsInfo, {item: item}),
                                React.createElement('span', {className: 'item-heading'}, item.headline ?
                                    item.headline.substr(0, 90) :
                                    item.type),
                                React.createElement('time', {}, moment(item.versioncreated).fromNow())
                            ),
                            React.createElement('div', {className: 'line'},
                                React.createElement('div', {className: 'state-label state-' + item.state}, item.state),
                                item.anpa_take_key ?
                                    React.createElement('div', {className: 'takekey'}, item.anpa_take_key) :
                                    null,
                                item.signal ?
                                    React.createElement('span', {className: 'signal'}, item.signal) :
                                    null,
                                broadcast.status ?
                                    React.createElement('span', {className: 'broadcast-status', tooltip: broadcast.status}, '!') :
                                    null,
                                flags.marked_for_not_publication ?
                                    React.createElement('div', {className: 'state-label not-for-publication'},
                                        gettext('Not for Publication')) :
                                    null,
                                flags.marked_for_legal ?
                                    React.createElement('div', {className: 'state-label legal'}, gettext('Legal')) :
                                    null,
                                anpa.name ?
                                    React.createElement('div', {className: 'category'}, anpa.name) :
                                    null,
                                React.createElement('span', {className: 'provider'}, provider.name),
                                item.is_spiked ?
                                    React.createElement('div', {className: 'expires'},
                                        gettext('expires') + ' ' + moment(item.expiry).fromNow()) :
                                    null,
                                item.archived ? React.createElement(FetchedDesksInfo, {item: item}) : null,
                                React.createElement(ItemContainer, {item: item, desk: props.desk})
                            )
                        );
                    };

                    var ItemUrgency = function(props) {
                        var urgency = props.urgency || 3;
                        return React.createElement(
                            'span',
                            {className: 'urgency-label urgency-label--' + urgency},
                            urgency
                        );
                    };

                    var BroadcastStatus = function(props) {
                        var broadcast = props.broadcast || {};
                        return React.createElement(
                            'span',
                            {className: 'broadcast-status', tooltip: broadcast.status},
                            '!'
                        );
                    };

                    var ActionsMenu = React.createClass({
                        toggle: function(event) {
                            this.setState({open: !this.state.open});
                            this.stopEvent(event);
                        },

                        stopEvent: function(event) {
                            event.stopPropagation();
                        },

                        getInitialState: function() {
                            return {open: false};
                        },

                        getActions: function() {
                            var item = this.props.item;
                            var type = this.getType();
                            var intent = {action: 'list', type: type};
                            var groups = {};
                            superdesk.findActivities(intent, item).forEach(function(activity) {
                                if (workflowService.isActionAllowed(item, activity.action)) {
                                    var group = activity.group || 'default';
                                    groups[group] = groups[group] || [];
                                    groups[group].push(activity);
                                }
                            });
                            return groups;
                        },

                        getType: function() {
                            return archiveService.getType(this.props.item);
                        },

                        groups: [
                            {_id: 'default', label: gettext('Actions')},
                            {_id: 'packaging', label: gettext('Packaging')},
                            {_id: 'highlights', label: gettext('Highlights')},
                            {_id: 'corrections', label: gettext('Corrections')}
                        ],

                        render: function() {
                            var menu = [];
                            var item = this.props.item;

                            var createAction = function(activity) {
                                return React.createElement(ActionsMenu.Item, {
                                    item: item,
                                    activity: activity,
                                    key: activity._id
                                });
                            }.bind(this);

                            if (this.state.open) {
                                var actions = this.getActions();
                                this.groups.map(function(group) {
                                    if (actions[group._id]) {
                                        menu.push(
                                            React.createElement(ActionsMenu.Label, {
                                                label: group.label,
                                                key: 'group-label-' + group._id
                                            }),
                                            React.createElement(ActionsMenu.Divider, {
                                                key: 'group-divider-' + group._id
                                            })
                                        );

                                        menu.push.apply(menu, actions[group._id].map(createAction));
                                    }
                                });
                            }

                            return React.createElement(
                                'div',
                                {className: 'item-right toolbox'},
                                React.createElement(
                                    'div',
                                    {className: 'item-actions-menu dropdown-big open'},
                                    React.createElement(
                                        'button',
                                        {
                                            className: 'more-activity-toggle condensed dropdown-toggle',
                                            onClick: this.toggle,
                                            onDblClick: this.stopEvent
                                        },
                                        React.createElement('i', {className: 'icon-dots-vertical'})
                                    ),
                                    React.createElement(
                                        'ul',
                                        {
                                            className: 'dropdown dropdown-menu more-activity-menu open',
                                            style: {top: '66%', left: -160, display: this.state.open ? 'block' : 'none', minWidth: 200}
                                        },
                                        menu
                                    )
                                )
                            );
                        }
                    });

                    ActionsMenu.Label = function(props) {
                        return React.createElement(
                            'li',
                            null,
                            React.createElement('div', {className: 'menu-label'}, props.label)
                        );
                    };

                    ActionsMenu.Divider = function() {
                        return React.createElement('li', {className: 'divider'});
                    };

                    ActionsMenu.Item = React.createClass({
                        run: function(event) {
                            activityService.start(this.props.activity, {data: {item: this.props.item}});
                        },

                        render: function() {
                            var activity = this.props.activity;
                            return React.createElement(
                                'li',
                                null,
                                React.createElement(
                                    'a',
                                    {title: gettext(activity.label), onClick: this.run},
                                    React.createElement('i', {className: 'icon-' + activity.icon}),
                                    React.createElement('span', {style: {display: 'inline'}}, gettext(activity.label))
                                )
                            );
                        }
                    });

                    var ProgressBar = function(props) {
                        return React.createElement('div', {className: 'archiving-progress', style: {width: props.completed + '%'}});
                    };

                    var ErrorBox = function(props) {
                        return React.createElement('div', {className: 'error-box'},
                            React.createElement('p', {className: 'message'}, gettext('There was an error archiving this item')),
                            React.createElement('div', {className: 'buttons'})
                        );
                    };

                    /**
                     * Item component
                     */
                    var Item = React.createClass({
                        shouldComponentUpdate: function(nextProps, nextState) {
                            return nextProps.item !== this.props.item ||
                                nextProps.view !== this.props.view ||
                                nextProps.flags.selected !== this.props.flags.selected ||
                                nextState !== this.state;
                        },

                        select: function() {
                            this.props.onSelect(this.props.item);
                        },

                        getInitialState: function() {
                            return {hover: false};
                        },

                        setHoverState: function() {
                            this.setState({hover: true});
                        },

                        unsetHoverState: function() {
                            this.setState({hover: false});
                        },

                        render: function() {
                            var item = this.props.item;
                            var broadcast = item.broadcast || {};
                            var contents = [
                                'div',
                                {
                                    className: classNames(
                                        'media-box',
                                        'media-' + item.type,
                                        {
                                            locked: item.lock_user && item.lock_session,
                                            selected: this.props.flags.selected,
                                            archived: item.archived || item.created
                                        }
                                    )

                                }
                            ];

                            if (item._progress) {
                                contents.push(React.createElement(ProgressBar, {completed: item._progress}));
                            }

                            if (this.props.view === 'mgrid') {
                                contents.push(
                                    item.archiveError ? React.createElement(ErrorBox) : null,
                                    React.createElement(MediaPreview, {
                                        item: item,
                                        desk: this.props.desk,
                                        onMultiSelect: this.props.onMultiSelect
                                    }),
                                    React.createElement(MediaInfo, {item: item, ingestProvider: this.props.ingestProvider}),
                                    React.createElement(GridTypeIcon, {item: item}),
                                    item.priority ? React.createElement(ItemPriority, {priority: item.priority}) : null,
                                    item.urgency ? React.createElement(ItemUrgency, {urgency: item.urgency}) : null,
                                    broadcast.status ? React.createElement(BroadcastStatus, {broadcast: broadcast}) : null,
                                    this.state.hover ? React.createElement(ActionsMenu, {item: item}) : null
                                );
                            } else {
                                contents.push(
                                    React.createElement('span', {className: 'state-border'}),
                                    React.createElement(ListTypeIcon, {
                                        item: item,
                                        onMultiSelect: this.props.onMultiSelect
                                    }),
                                    React.createElement(ListPriority, {item: item}),
                                    React.createElement(ListItemInfo, {
                                        item: item,
                                        desk: this.props.desk,
                                        ingestProvider: this.props.ingestProvider
                                    }),
                                    this.state.hover ? React.createElement(ActionsMenu, {item: item}) : null
                                );
                            }

                            return React.createElement(
                                'li',
                                {
                                    id: item._id,
                                    key: item._id,
                                    className: classNames('list-item-view', {active: this.props.flags.selected}),
                                    onMouseEnter: this.setHoverState,
                                    onMouseLeave: this.unsetHoverState,
                                    onClick: this.select
                                },
                                React.createElement.apply(null, contents)
                            );
                        }
                    });

                    var Keys = Object.freeze({
                        right: 39,
                        left: 37,
                        enter: 13
                    });

                    /**
                     * Item list component
                     */
                    var ItemList = React.createClass({
                        getInitialState: function() {
                            return {itemsList: [], itemsById: {}, selected: null, view: 'mgrid'};
                        },

                        multiSelect: function(item, selected) {
                            var itemsById = angular.extend({}, this.state.itemsById);
                            itemsById[item._id] = angular.extend({}, item, {selected: selected});
                            this.setState({itemsById: itemsById});
                            multi.toggle(itemsById[item._id]);
                        },

                        select: function(item) {
                            console.time('select');
                            $timeout.cancel(this.updateTimeout);
                            this.updateTimeout = $timeout(function() {
                                scope.$apply(function() {
                                    scope.preview(item);
                                });
                            }, 100, false);
                            this.setState({
                                selected: item._id
                            }, function() {
                                console.timeEnd('select');
                            });
                        },

                        updateItem: function(itemId, changes) {
                            var item = this.state.itemsById[itemId] || null;
                            if (item) {
                                var itemsById = angular.extend({}, this.state.itemsById);
                                itemsById[itemId] = angular.extend({}, item, changes);
                                this.setState({itemsById: itemsById});
                            }
                        },

                        getSelectedItem: function() {
                            var selected = this.state.selected;
                            return this.state.itemsById[selected];
                        },

                        handleKey: function(event) {
                            var diff;
                            if (event.keyCode === Keys.right) {
                                diff = 1;
                            } else if (event.keyCode === Keys.left) {
                                diff = -1;
                            }

                            if (event.keyCode === Keys.enter) {
                                if (this.state.selected) {
                                    this.select(this.getSelectedItem());
                                }

                                event.stopPropagation();
                                return;
                            }

                            if (diff != null) {
                                event.stopPropagation();
                                if (this.state.selected) {
                                    for (var i = 0; i < this.state.itemsList.length; i++) {
                                        if (this.state.itemsList[i] === this.state.selected) {
                                            var next = Math.min(this.state.itemsList.length - 1, Math.max(0, i + diff));
                                            this.select(this.state.itemsById[this.state.itemsList[next]]);
                                            return;
                                        }
                                    }
                                } else {
                                    this.select(this.state.itemsById[this.state.itemsList[0]]);
                                }
                            }
                        },

                        componentDidMount: function() {
                            ReactDOM.findDOMNode(this).focus();
                        },

                        render: function render() {
                            var createItem = function createItem(itemId) {
                                var item = this.state.itemsById[itemId];
                                var task = item.task || {desk: null};
                                return React.createElement(Item, {
                                    key: item._id,
                                    item: item,
                                    view: this.state.view,
                                    flags: {selected: this.state.selected === item._id},
                                    onSelect: this.select,
                                    onMultiSelect: this.multiSelect,
                                    ingestProvider: this.props.ingestProvidersById[item.ingest_provider] || null,
                                    desk: this.props.desksById[task.desk] || null
                                });
                            }.bind(this);

                            return React.createElement(
                                'ul',
                                {
                                    className: this.state.view + '-view list-view',
                                    onKeyDown: this.handleKey,
                                    tabIndex: '0'
                                },
                                this.state.itemsList.map(createItem)
                            );
                        }
                    });

                    /**
                     * Init react rendering
                     */
                    var listComponent;
                    scope.$applyAsync(function() {
                        var list = elem.find('.shadow-list-holder')[0];
                        var itemList = React.createElement(ItemList, {
                            ingestProvidersById: scope.ingestProvidersById,
                            desksById: scope.desksById,
                            highlightsById: scope.highlightsById
                        });

                        listComponent = ReactDOM.render(itemList, list);
                    });

                    scope.$on('item:lock', function(_e, data) {
                        listComponent.updateItem(data.item, {
                            lock_user: data.user,
                            lock_session: data.lock_session,
                            lock_time: data.lock_time
                        });
                    });

                    scope.$on('item:unlock', function(_e, data) {
                        listComponent.updateItem(data.item, {
                            lock_user: null,
                            lock_session: null,
                            lock_time: null
                        });
                    });

                    scope.$on('multi:reset', function(e, data) {
                        var itemsById = angular.extend({}, listComponent.state.itemsById);
                        var ids = data.ids || [];
                        ids.forEach(function(id) {
                            itemsById[id] = angular.extend({}, itemsById[id], {
                                selected: false
                            });
                        });

                        listComponent.setState({itemsById: itemsById});
                    });

                    /*
                     * Function for updating list after item has been deleted
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
                    scope.uuid = function(item) {
                        return search.generateTrackByIdentifier(item);
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

        /**
         * Opens and manages save search panel
         */
        .directive('sdSaveSearch', ['$location', 'asset', 'api', 'session', 'notify', 'gettext',
            function($location, asset, api, session, notify, gettext) {
            return {
                templateUrl: asset.templateUrl('superdesk-search/views/save-search.html'),
                link: function(scope, elem) {
                    scope.edit = null;
                    scope.activateSearchPane = false;

                    scope.$on('edit:search', function(event, args)  {
                        scope.activateSearchPane = false;
                        scope.edit = _.create(scope.editingSearch) || {};
                    });

                    scope.editItem = function () {
                        scope.activateSearchPane = true;
                        scope.edit = _.create(scope.editingSearch) || {};
                    };

                    scope.saveas = function() {
                        scope.activateSearchPane = true;
                        scope.edit = _.clone(scope.editingSearch) || {};
                        delete scope.edit._id;
                        scope.edit.name = '';
                        scope.edit.description = '';
                    };

                    scope.cancel = function () {
                        scope.sTab = scope.editingSearch ? false : true;
                        scope.resetEditingSearch();
                        scope.edit = null;
                        scope.activateSearchPane = false;
                    };

                    scope.clear = function() {
                        scope.resetEditingSearch();
                        scope.edit = null;
                        $location.url('/search');
                    };

                    /**
                     * Patches or posts the given search
                     */
                    scope.save = function(editSearch) {

                        function onSuccess() {
                            notify.success(gettext('Saved search is saved successfully'));
                            scope.cancel();
                            scope.sTab = false;
                            scope.edit = null;
                        }

                        function onFail(error) {
                            scope.edit = null;
                            if (angular.isDefined(error.data._message)) {
                                notify.error(error.data._message);
                            } else {
                                notify.error(gettext('Error. Saved search could not be saved.'));
                            }
                        }

                        var search = getFilters(_.clone($location.search()));
                        editSearch.filter = {query: search};
                        var originalSearch = {};

                        if (editSearch._id) {
                            originalSearch = scope.editingSearch;
                        }

                        api('saved_searches', session.identity).save(originalSearch, editSearch).then(onSuccess, onFail);
                    };

                    /**
                     * Converts the integer fields: priority and urgency to objects
                     * within a given search
                     *
                     * @return {Object} the updated search object
                     */
                    function getFilters(search) {
                        _.forOwn(search, function(value, key) {
                            if (_.contains(['priority', 'urgency'], key)) {
                                search[key] = JSON.parse(value);
                            }
                        });

                        return search;
                    }
                }
            };
        }])

        .directive('sdItemContainer', ['$filter', 'desks', 'api', function($filter, desks, api) {
            return {
                scope: {
                    item: '='
                },
                template: '<span class="location-desk-label">{{item.label}}</span> {{item.value}}',
                link: function(scope, elem) {
                    if (scope.item._type !== 'ingest') {
                        if (scope.item.task && scope.item.task.desk) {
                            desks.initialize().then(function() {
                                if (desks.deskLookup[scope.item.task.desk]) {
                                    scope.item.label = 'desk:';
                                    scope.item.value = desks.deskLookup[scope.item.task.desk].name;
                                }
                            });
                        } else {
                            if (scope.item._type === 'archive') {
                                scope.item.label = 'location:';
                                scope.item.value = 'workspace';
                            } else {
                                if (scope.item._type === 'published' && scope.item.allow_post_publish_actions === false) {
                                    scope.item.label = '';
                                    scope.item.value = 'archived';
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
            'gettext', 'keyboardManager', 'asset', 'authoringWorkspace', 'authoring',
            function(superdesk, session, $location, search, api, notify, gettext, keyboardManager, asset, authoringWorkspace, authoring) {
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
                            if (authoring.itemActions(items[0]).edit) {
                                authoringWorkspace.edit(items[0]);
                            } else {
                                authoringWorkspace.view(items[0]);
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
                        scope.$applyAsync(function() {
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

        .directive('sdItemSearch', ['$location', '$timeout', 'asset', 'api', 'tags', 'search', 'metadata',
            'desks', 'userList', 'searchProviderService', '$filter',
            function($location, $timeout, asset, api, tags, search, metadata, desks,
                     userList, searchProviderService, $filter) {
                return {
                    scope: {
                        repo: '=',
                        context: '='
                    },
                    templateUrl: asset.templateUrl('superdesk-search/views/item-search.html'),
                    link: function(scope, elem) {

                        var input = elem.find('#search-input');

                        /*
                         * init function to setup the directive initial state and called by $locationChangeSuccess event
                         * @param {boolean} load_data.
                         */
                        function init(load_data) {
                            var params = $location.search();
                            scope.query = params.q;
                            scope.flags = false;
                            scope.meta = {};
                            scope.fields = {};
                            scope.searchProviderTypes = searchProviderService.getProviderTypes();

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
                                if (!scope.repo.archive && !scope.repo.ingest &&
                                    !scope.repo.published && !scope.repo.archived) {
                                    scope.repo.search = params.repo;
                                } else {
                                    scope.repo.search = 'local';
                                }
                            }

                            if ($location.search().unique_name) {
                                scope.fields.unique_name = $location.search().unique_name;
                            }

                            if (load_data) {
                                fetchProviders();
                                fetchUsers();
                                fetchDesks();
                            } else {
                                initializeDesksDropDown();
                            }
                        }

                        init(true);

                        /*
                         * Initialize the creator drop down selection.
                         */
                        function fetchUsers() {
                            userList.getAll()
                            .then(function(result) {
                                scope.userList = {};
                                _.each(result, function(user) {
                                    scope.userList[user._id] = user;
                                });

                                if ($location.search().original_creator) {
                                    scope.fields.original_creator = $location.search().original_creator;
                                }
                            });
                        }

                        /*
                         * Initialize the search providers
                         */
                        function fetchProviders() {
                            return api.search_providers.query({max_results: 200})
                                .then(function(result) {
                                    scope.providers = $filter('sortByName')(result._items, 'search_provider');
                                });
                        }

                        /*
                         * Initialize the desk drop down
                         */
                        function fetchDesks() {
                            scope.desks = [];
                            desks.initialize()
                                .then(function() {
                                    scope.desks = desks.desks;
                                    initializeDesksDropDown();
                                });
                        }

                        /*
                         *  Initialize Desks DropDown
                         */
                        function initializeDesksDropDown() {
                            if (scope.desks && scope.desks._items) {
                                initFromToDesk($location.search().from_desk, 'from_desk');
                                initFromToDesk($location.search().to_desk, 'to_desk');
                            }
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
                                    scope.fields[field] = deskParams[0];
                                }
                            }
                        }

                        scope.$on('$locationChangeSuccess', function() {
                            if (scope.query !== $location.search().q ||
                                scope.fields.from_desk !== $location.search().from_desk ||
                                scope.fields.to_desk !== $location.search().to_desk ||
                                scope.fields.unique_name !== $location.search().unique_name ||
                                scope.fields.original_creator !== $location.search().original_creator) {
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

                        /*
                         * Get Query function build the query string
                         */
                        function getQuery() {
                            var metas = [];
                            angular.forEach(scope.meta, function(val, key) {
                                val = val.replace(/[()]/g, '');
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

                            angular.forEach(scope.fields, function(val, key) {
                                if (key === 'from_desk') {
                                    $location.search('from_desk', getDeskParam('from_desk'));
                                } else if (key === 'to_desk') {
                                    $location.search('to_desk', getDeskParam('to_desk'));
                                } else {
                                    $location.search(key, val);
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
                         * Get the Desk Type
                         * @param {string} field from or to
                         * @returns {string} desk querystring parameter
                         */
                        function getDeskParam(field) {
                            var deskId = '';
                            if (scope.fields[field]) {
                                deskId = scope.fields[field];
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
                                    var addItemSubjectName = 'subject.qcode:(' + item.subject[item.subject.length - 1].qcode + ')',
                                        q = (scope.query ? scope.query + ' ' + addItemSubjectName : addItemSubjectName);

                                    $location.search('q', q);
                                } else {
                                    /* Removing subject codes from filter */
                                    var params = $location.search();
                                    if (params.q) {
                                        for (var j = 0; j < subjectCodes.length; j++) {
                                            if (item.subject.indexOf(subjectCodes[j]) === -1) {
                                                var removeItemSubjectName = 'subject.qcode:(' + subjectCodes[j].qcode + ')';
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
            }
        ])

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
                    api.query('saved_searches', {'max_results': 200}, session.identity).then(function(res) {
                        scope.searches = res._items;
                    });
                }
            };
        }])

        .directive('sdSavedSearches', ['$rootScope', 'api', 'session', 'notify', 'gettext', 'asset', '$location', 'desks', 'privileges',
        function($rootScope, api, session, notify, gettext, asset, $location, desks, privileges) {
            return {
                templateUrl: asset.templateUrl('superdesk-search/views/saved-searches.html'),
                scope: {},
                link: function(scope) {

                    var resource = api('saved_searches', session.identity);
                    scope.selected = null;
                    scope.searchText = null;
                    scope.userSavedSearches = [];
                    scope.globalSavedSearches = [];
                    scope.privileges = privileges.privileges;
                    var originalUserSavedSearches = [];
                    var originalGlobalSavedSearches = [];

                    desks.initialize()
                    .then(function() {
                        scope.userLookup = desks.userLookup;
                    });

                    function initSavedSearches() {
                        resource.query({'max_results': 200}).then(function(searches) {
                            scope.userSavedSearches.length = 0;
                            scope.globalSavedSearches.length = 0;
                            scope.searches = searches._items;
                            _.forEach(scope.searches, function(search) {
                                if (search.user === session.identity._id) {
                                    scope.userSavedSearches.push(setFilters(search));
                                } else if (search.is_global) {
                                    scope.globalSavedSearches.push(setFilters(search));
                                }
                            });
                            originalUserSavedSearches = _.clone(scope.userSavedSearches);
                            originalGlobalSavedSearches = _.clone(scope.globalSavedSearches);
                        });
                    }

                    initSavedSearches();

                    scope.select = function(search) {
                        scope.selected = search;
                        $location.search(search.filter.query);
                    };

                    /**
                     * Converts the integer fields to string
                     * within a given search
                     *
                     * @return {Object} the updated search object
                     */
                    function setFilters(search) {
                        _.forOwn(search.filter.query, function(value, key) {
                            if (_.contains(['priority', 'urgency'], key)) {
                                search.filter.query[key] = JSON.stringify(value);
                            }
                        });

                        return search;
                    }

                    scope.edit = function(search) {
                        scope.select(search);
                        $rootScope.$broadcast('edit:search', search);
                    };

                    /**
                     * Filters the content of global and user filters
                     *
                     */
                    scope.filter = function() {
                        scope.userSavedSearches = _.clone(originalUserSavedSearches);
                        scope.globalSavedSearches = _.clone(originalGlobalSavedSearches);

                        if (scope.searchText || scope.searchText !== '') {
                            scope.userSavedSearches = _.filter(originalUserSavedSearches, function(n) {
                                return n.name.toUpperCase().indexOf(scope.searchText.toUpperCase()) >= 0;
                            });

                            scope.globalSavedSearches = _.filter(originalGlobalSavedSearches, function(n) {
                                return n.name.toUpperCase().indexOf(scope.searchText.toUpperCase()) >= 0;
                            });
                        }
                    };

                    scope.remove = function(searches) {
                        resource.remove(searches).then(function() {
                            notify.success(gettext('Saved search removed'));
                            initSavedSearches();
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
                        return openItem && openItem.type === type;
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
                sideTemplateUrl: 'scripts/superdesk-workspace/views/workspace-sidenav.html',
                controller: ['$scope', 'ingestProvidersById', 'desksById', 'highlightsById',
                function($scope, ingestProvidersById, desksById, highlightsById) {
                    $scope.ingestProvidersById = ingestProvidersById;
                    $scope.desksById = desksById;
                    $scope.highlightsById = highlightsById;
                }],
                resolve: {
                    ingestProvidersById: ['ingestSources', function(ingestSources) {
                        return ingestSources.initialize().then(function() {
                            return ingestSources.providersLookup;
                        });
                    }],
                    desksById: ['desks', function(desks) {
                        return desks.initialize().then(function() {
                            return desks.deskLookup;
                        });
                    }],
                    highlightsById: ['highlightsService', function(highlightsService) {
                        return highlightsService.get().then(function(result) {
                            var highlights = {};
                            result._items.forEach(function(item) {
                                highlights[item._id] = item;
                            });
                            return highlights;
                        });
                    }]
                }
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
                canSpike = canSpike && authoring.itemActions(item).spike && !item.lock_user;
            });
            return canSpike;
        };

        this.canPackageItems = function() {
            var canPackage = true;
            multi.getItems().forEach(function(item) {
                canPackage = canPackage && item.state !== 'killed';
            });
            return canPackage;
        };
    }
})();
