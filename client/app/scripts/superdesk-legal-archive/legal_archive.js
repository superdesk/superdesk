(function() {
    'use strict';

    LegalArchiveService.$inject = ['$q', 'api', 'notify', '$location', 'gettext'];
    function LegalArchiveService($q, api, notify, $location, gettext) {
        var DEFAULT_PER_PAGE = 25;
        this.default_items = Object.freeze({_meta: {max_results: DEFAULT_PER_PAGE, page: 1, total: 1}});

        var sortOptions = [
            {field: 'versioncreated', label: gettext('Updated')},
            {field: 'firstcreated', label: gettext('Created')},
            {field: 'urgency', label: gettext('News Value')},
            {field: 'anpa_category.name', label: gettext('Category')},
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

        function formatSort(key, dir) {
            var val = dir === 'asc' ? 1 : -1;
            return '[("' + encodeURIComponent(key) + '", ' + val + ')]';
        }

        function setSortSearch(field, dir) {
            $location.search('sort', field + ':' + dir);
            $location.search('page', null);
        }

        sort('versioncreated');

        // sort public api
        this.setSort = sort;
        this.getSort = getSort;
        this.sortOptions = sortOptions;
        this.toggleSortDir = toggleSortDir;

        this.getCriteria = function() {
            var params = $location.search(),
                criteria = {
                    max_results: Number(params.max_results) || DEFAULT_PER_PAGE
                };

            if (params.q) {
                criteria.where = params.q;
            }

            if (params.page) {
                criteria.page = parseInt(params.page, 10);
            }

            if (params.sort) {
                var sort = params.sort.split(':');
                criteria.sort = formatSort(sort[0], sort[1]);
            }

            return criteria;
        };

        this.updateSearchQuery = function updateSearchQuery(search) {
            var where = [];

            function prepareDate(val) {
                return _.trunc(val, {'length': val.length - 3, 'omission': ''}) + '00';
            }

            _.forEach(search, function(n, key) {
                var val = _.trim(n);
                if (val) {
                    var clause = {};
                    if (key === 'published_after')
                    {
                        clause.versioncreated = {'$gte': prepareDate(val)};
                    } else if (key === 'published_before')
                    {
                        clause.versioncreated = {'$lte': prepareDate(val)};
                    } else {
                        clause[key] = {'$regex': val, '$options': '-i'};
                    }
                    where.push(clause);
                }
            });

            var where_clause = null;

            if (where.length === 1) {
                where_clause = JSON.stringify(where[0]);
            } else if (where.length > 1) {
                where_clause = JSON.stringify({
                    '$and': where
                });
            }
            $location.search('q', where_clause);
            return where_clause;
        };

        // query public api
        this.query = function query() {
            var search_criteria = this.getCriteria();
            return api.legal_archive.query(search_criteria);
        };
    }

    LegalArchiveController.$inject = ['$scope', '$location', 'legal'];
    function LegalArchiveController($scope, $location, legal) {
        $scope.criteria = {};
        $scope.items = legal.default_items;
        $scope.loading = false;
        $scope.selected = {};

        $scope.search = function () {
            legal.updateSearchQuery($scope.criteria);
            refresh();
        };

        function refresh () {
            $scope.loading = true;
            legal.query().then(function(items) {
                $scope.loading = false;
                $scope.items = items;
            });
        }

        $scope.preview = function(selectedItem) {
            $scope.selected.preview = selectedItem;
        };

        $scope.openLightbox = function () {
            $scope.selected.view = $scope.selected.preview;
        };

        $scope.closeLightbox = function () {
            $scope.selected.view = null;
        };

        $scope.clear = function () {
            legal.criteria = $scope.criteria = {};
            $scope.items = legal.default_items;
        };

        $scope.$watch(function getSearchParams() {
            return _.omit($location.search(), '_id');
        }, refresh, true);

        $scope.search();
    }

    var app = angular.module('superdesk.legal_archive', [
        'superdesk.activity',
        'superdesk.api'
    ]);

    app
        .service('legal', LegalArchiveService)
        .directive('sdLegalItemSortbar', ['legal', 'asset', function sortBarDirective(legal, asset) {
            return {
                scope: {},
                templateUrl: asset.templateUrl('superdesk-search/views/item-sortbar.html'),
                link: function(scope) {
                    scope.sortOptions = legal.sortOptions;

                    function getActive() {
                        scope.active = legal.getSort();
                    }

                    scope.sort = function sort(field) {
                        legal.setSort(field);
                    };

                    scope.toggleDir = function toggleDir($event) {
                        legal.toggleSortDir();
                    };

                    scope.$on('$routeUpdate', getActive);
                    getActive();
                }
            };
        }])
        .config(['apiProvider', function(apiProvider) {
            apiProvider.api('legal_archive', {
                type: 'http',
                backend: {rel: 'legal_archive'}
            });
            apiProvider.api('legal_archive_versions', {
                type: 'http',
                backend: {rel: 'legal_archive_versions'}
            });
        }])
        .config(['superdeskProvider', function(superdesk) {
            superdesk
                .activity('/legal_archive/', {
                    label: gettext('Legal Archive'),
                    description: gettext('Confidential data'),
                    priority: 100,
                    beta: true,
                    controller: LegalArchiveController,
                    templateUrl: 'scripts/superdesk-legal-archive/views/legal_archive.html',
                    sideTemplateUrl: 'scripts/superdesk-dashboard/views/workspace-sidenav.html',
                    category: superdesk.MENU_MAIN,
                    reloadOnSearch: false,
                    filters: [],
                    privileges: {legal_archive: 1}
                });
        }]);

    return app;
})();
