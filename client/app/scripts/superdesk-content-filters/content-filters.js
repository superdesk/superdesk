/**
 * This file is part of Superdesk.
 *
 * Copyright 2013, 2014, 2015 Sourcefabric z.ú. and contributors.
 *
 * For the full copyright and license information, please see the
 * AUTHORS and LICENSE files distributed with this source code, or
 * at https://www.sourcefabric.org/superdesk/license
 */

(function() {
    'use strict';

    /**
     * @memberof superdesk.content_filters
     * @ngdoc service
     * @name contentFilters
     * @description
     *   This service implements a convenience layer on top of the server API,
     *   providing higher-level methods for fetching and modifying all content
     *   related to content filters on the server.
     */
    ContentFiltersService.$inject = ['api', '$filter'];
    function ContentFiltersService(api, $filter) {

        this.productionTestFilter = function(filter) {
            return filter;
        };

        this.getFilterConditionParameters = function() {
            return api.query('filter_conditions/parameters')
                .then(angular.bind(this, function(params) {
                    return params._items;
                }));
        };

        this.saveFilterCondition = function(orig, diff) {
            return api.save('filter_conditions', orig, diff);
        };

        this.remove = function(item) {
            return api.remove(item);
        };

        this.getAllFilterConditions = function(page, items) {
            return _getAll('filter_conditions', page, items);
        };

        this.getFilterSearchResults = function(inputParams) {
            //call api to get search results
            return api.query('subscribers', {'filter_condition': inputParams})
                .then(angular.bind(this, function(resultSet) {
                    return resultSet._items;
                }));
        };

        this.getAllContentFilters = function(page, items) {
            return _getAll('content_filters', page, items);
        };

        this.saveContentFilter = function(orig, diff) {
            return api.save('content_filters', orig, diff);
        };

        this.testContentFilter = function(diff) {
            return api.save('content_filter_tests', {}, diff);
        };

        this.getGlobalContentFilters = function() {
            return api.query('content_filters', {'is_global': true}).then(function(response) {
                return $filter('sortByName')(response._items);
            });
        };

        var _getAll = function(endPoint, page, items) {
            page = page || 1;
            items = items || [];

            return api(endPoint)
            .query({max_results: 200, page: page})
            .then(function(result) {
                items = items.concat(result._items);
                if (result._links.next) {
                    page++;
                    return _getAll(page, items);
                }
                return items;
            });
        };
    }

    /**
     * @memberof superdesk.content_filters
     * @ngdoc controller
     * @name ContentFiltersConfigCtrl
     * @description
     *   Main controller for the Content Filters page under the system
     *   settings section.
     */
    ContentFiltersConfigController.$inject = [];
    function ContentFiltersConfigController () {
        var self = this;

        self.TEMPLATES_DIR = 'scripts/superdesk-content-filters/views';
        self.activeTab = 'filters';

        /**
        * Sets the active tab name to the given value.
        *
        * @method changeTab
        * @param {string} newTabName - name of the new active tab
        */
        self.changeTab = function (newTabName) {
            self.activeTab = newTabName;
        };
    }

    /**
     * @memberof superdesk.content_filters
     * @ngdoc controller
     * @name FilterConditionsCtrl
     * @description
     *   Controller for the Filter Conditions tab, found on the Content Filters
     *   settings page.
     */
    FilterConditionsController.$inject = ['$scope', 'contentFilters', 'notify', 'modal', '$filter'];
    function FilterConditionsController($scope, contentFilters, notify, modal, $filter) {
        $scope.filterConditions = null;
        $scope.filterCondition = null;
        $scope.origFilterCondition = null;
        $scope.filterConditionParameters = null;
        $scope.operatorLookup = {};
        $scope.valueLookup = {};
        $scope.valueFieldLookup = {};

        $scope.edit = function(fc) {
            contentFilters.getFilterConditionParameters().then(function(params) {
                $scope.filterConditionParameters = params;
                _.each(params, function(param) {
                    $scope.operatorLookup[param.field] = param.operators;
                    $scope.valueLookup[param.field] = param.values;
                    $scope.valueFieldLookup[param.field] = param.value_field;
                });

                $scope.origFilterCondition = fc || {};
                $scope.filterCondition = _.create($scope.origFilterCondition);
                $scope.filterCondition.values = [];
                setFilterValues();
            });
        };

        $scope.isListValue = function() {
            return _.contains(['in', 'nin'], $scope.filterCondition.operator) && $scope.valueLookup[$scope.filterCondition.field];
        };

        $scope.cancel = function() {
            $scope.origFilterCondition = null;
            $scope.filterCondition = null;
        };

        $scope.save = function() {
            $scope.filterCondition.value = getFilterValue();
            delete $scope.filterCondition.values;
            contentFilters.saveFilterCondition($scope.origFilterCondition, $scope.filterCondition)
                .then(
                    function() {
                        notify.success(gettext('Filter condition saved.'));
                        $scope.cancel();
                    },
                    function(response) {
                        if (angular.isDefined(response.data._issues)) {
                            if (response.data._issues.name && response.data._issues.name.unique) {
                                notify.error(gettext('Error: ' + gettext('Name needs to be unique')));
                            } else {
                                notify.error(gettext('Error: ' + JSON.stringify(response.data._issues)));
                            }
                        } else if (angular.isDefined(response.data._message)) {
                            notify.error(gettext('Error: ' + response.data._message));
                        } else {
                            notify.error(gettext('Error: Failed to save filter condition.'));
                        }
                    }
                ).then(fetchFilterConditions);
        };

        $scope.remove = function(filterCondition) {
            modal.confirm(gettext('Are you sure you want to delete filter condition?'))
            .then(function() {
                return contentFilters.remove(filterCondition);
            })
            .then(function(result) {
                _.remove($scope.filterConditions, filterCondition);
            }, function(response) {
                if (angular.isDefined(response.data._message)) {
                    notify.error(gettext('Error: ' + response.data._message));
                } else {
                    notify.error(gettext('There is an error. Filter condition cannot be deleted.'));
                }
            });
        };

        var getFilterValue = function() {
            if ($scope.isListValue()) {
                var values = [];
                _.each($scope.filterCondition.values, function(value) {
                    values.push(value[$scope.valueFieldLookup[$scope.filterCondition.field]]);
                });
                return values.join();
            } else {
                return $scope.filterCondition.value;
            }
        };

        var setFilterValues = function() {
            if ($scope.isListValue()) {
                var values = $scope.filterCondition.value.split(',');
                var all_values = $scope.valueLookup[$scope.filterCondition.field];
                var value_field = $scope.valueFieldLookup[$scope.filterCondition.field];

                _.each(values, function(value) {
                    var v = _.find(all_values, function(val) {
                        return val[value_field].toString() === value;
                    });

                    $scope.filterCondition.values.push(v);
                });
            }
        };

        var fetchFilterConditions = function() {
            contentFilters.getAllFilterConditions().then(function(_filterConditions) {
                $scope.filterConditions = $filter('sortByName')(_filterConditions);
            });
        };

        fetchFilterConditions();

    }

    /**
     * @memberof superdesk.content_filters
     * @ngdoc controller
     * @name ManageContentFiltersCtrl
     * @description
     *   Controller for the Filters tab, found on the Content Filters settings
     *   page.
     */
    ManageContentFiltersController.$inject = ['$scope', 'contentFilters', 'notify', 'modal', '$filter'];
    function ManageContentFiltersController($scope, contentFilters, notify, modal, $filter) {
        $scope.filterConditions = null;
        $scope.contentFilters = null;
        $scope.contentFilter = null;
        $scope.origContentFilter = null;
        $scope.preview = null;
        $scope.filterConditionLookup = {};
        $scope.contentFiltersLookup = {};

        $scope.editFilter = function(pf) {
            $scope.origContentFilter = pf || {};
            $scope.contentFilter = _.create($scope.origContentFilter);
            $scope.contentFilter.name =  $scope.origContentFilter.name;
            $scope.contentFilter.content_filter = _.cloneDeep($scope.origContentFilter.content_filter);
            initContentFilter();
            $scope.previewContentFilter();
        };

        $scope.close = function() {
            $scope.previewContentFilter();
            $scope.origContentFilter = null;
            $scope.contentFilter = null;
            $scope.test.test_result = null;
            $scope.test.article_id = null;
        };

        $scope.saveFilter = function() {
            delete $scope.contentFilter.article_id;
            contentFilters.saveContentFilter($scope.origContentFilter, $scope.contentFilter)
                .then(
                    function() {
                        notify.success(gettext('Content filter saved.'));
                        $scope.close();
                    },
                    function(response) {
                        if (angular.isDefined(response.data._issues) &&
                            angular.isDefined(response.data._issues['validator exception'])) {
                            notify.error(gettext('Error: ' + response.data._issues['validator exception']));
                        } else if (angular.isDefined(response.data._issues)) {
                            if (response.data._issues.name && response.data._issues.name.unique) {
                                notify.error(gettext('Error: ' + gettext('Name needs to be unique')));
                            } else {
                                notify.error(gettext('Error: ' + JSON.stringify(response.data._issues)));
                            }
                        } else if (angular.isDefined(response.data._message)) {
                            notify.error(gettext('Error: ' + response.data._message));
                        } else if (response.status === 500) {
                            notify.error(gettext('Error: Internal error in Filter testing'));
                        } else {
                            notify.error(gettext('Error: Failed to test content filter.'));
                        }
                    }
                ).then(fetchContentFilters);
        };

        $scope.remove = function(pf) {
            modal.confirm(gettext('Are you sure you want to delete content filter?'))
            .then(function() {
                return contentFilters.remove(pf);
            })
            .then(function(result) {
                _.remove($scope.contentFilters, pf);
            }, function(response) {
                if (angular.isDefined(response.data._message)) {
                    notify.error(gettext('Error: ' + response.data._message));
                } else {
                    notify.error(gettext('There is an error. Content filter cannot be deleted.'));
                }
            });
        };

        $scope.addStatement = function() {
            $scope.contentFilter.content_filter.push({'expression': {}});
        };

        $scope.removeStatement = function(index) {
            $scope.contentFilter.content_filter.splice(index, 1);
            $scope.previewContentFilter();
        };

        $scope.addFilter = function(filterRow, filterType) {
            if (!(filterType in filterRow.expression)) {
                filterRow.expression[filterType] = [];
            }

            if (filterRow.selected && !_.includes(filterRow.expression[filterType], filterRow.selected)) {
                filterRow.expression[filterType].push(filterRow.selected);
                delete filterRow.selected;
                $scope.previewContentFilter();
            }
        };

        $scope.removeFilter = function(filterRow, filterId, filterType) {
            filterRow.expression[filterType] = _.without(filterRow.expression[filterType], filterId);
            $scope.previewContentFilter();
        };

        $scope.productionTest = function (filter) {
            $scope.$broadcast('triggerTest', filter);
        };

        $scope.test = function() {

            if (!$scope.test.article_id) {
                notify.error(gettext('Please provide an article id'));
                return;
            }

            contentFilters.testContentFilter({'filter': $scope.contentFilter, 'article_id': $scope.test.article_id})
                .then(
                    function(result) {
                        $scope.test.test_result = result.match_results ? 'Does Match' : 'Doesn\'t Match';
                    },
                    function(response) {
                        if (angular.isDefined(response.data._issues)) {
                            notify.error(gettext('Error: ' + response.data._issues));
                        } else if (angular.isDefined(response.data._message)) {
                            notify.error(gettext('Error: ' + response.data._message));
                        } else {
                            notify.error(gettext('Error: Failed to save content filter.'));
                        }
                    }
                );
        };

        $scope.previewContentFilter = function() {
            $scope.preview = parseContentFilter($scope.contentFilter.content_filter);
        };

        var parseContentFilter = function(contentFilter) {
            var previews = [];
            _.each(contentFilter, function(filterRow) {
                var statementPreviews = [];

                if ('pf' in filterRow.expression) {
                    _.each(filterRow.expression.pf, function(filterId) {
                        var f = $scope.contentFiltersLookup[filterId];
                        statementPreviews.push(parseContentFilter(f.content_filter));
                    });
                }

                if ('fc' in filterRow.expression) {
                    _.each(filterRow.expression.fc, function(filterId) {
                        var f = $scope.filterConditionLookup[filterId];
                        statementPreviews.push('(' + f.field + ' ' + f.operator + ' "' + f.value + '")');
                    });
                }

                if (statementPreviews.length > 0) {
                    previews.push('[' + statementPreviews.join(' AND ') + ']');
                }
            });

            if (previews.length > 0) {
                return previews.join(' OR ');
            }

            return '';
        };

        var initContentFilter = function() {
            if (!$scope.contentFilter.content_filter || $scope.contentFilter.content_filter.length === 0)
            {
                $scope.contentFilter.content_filter = [{'expression': {}}];
            }
        };

        var fetchFilterConditions = function() {
            contentFilters.getAllFilterConditions().then(function(_filterConditions) {
                $scope.filterConditions = $filter('sortByName')(_filterConditions);
                _.each(_filterConditions, function(filter) {
                    $scope.filterConditionLookup[filter._id] = filter;
                });
            });
        };

        var fetchContentFilters = function() {
            contentFilters.getAllContentFilters().then(function(_filters) {
                $scope.contentFilters = $filter('sortByName')(_filters);

                _.each($scope.contentFilters, function(filter) {
                    $scope.contentFiltersLookup[filter._id] = filter;
                });
            });
        };

        fetchFilterConditions();
        fetchContentFilters();
    }

    /**
     * @memberof superdesk.content_filters
     * @ngdoc directive
     * @name sdManageFiltersTab
     * @description
     *   A directive that simply loads the view for managing content filters and
     *   connects it with its controller (ManageContentFiltersCtrl).
     */
    function manageFiltersTabDirective () {
        return {
            templateUrl: 'scripts/superdesk-content-filters/views/manage-filters.html',
            controller: ManageContentFiltersController
        };
    }

    /**
     * @memberof superdesk.content_filters
     * @ngdoc controller
     * @name ProductionTestCtrl
     * @description
     *   Controller for the modal page used for testing a content filter
     *   against existing content items. Triggered by the action under the
     *   Filters tab on the Content Filters settings page.
     */
    ProductionTestController.$inject = ['$scope', 'contentFilters', 'notify', '$location', '$window'];
    function ProductionTestController($scope, contentFilters, notify, $location, $window) {
        $scope.preview = null;
        $scope.selected = {};
        $scope.selectedItem = {};
        $scope.selectedfilter = null;
        $scope.testResult = null;
        var UP = -1,
        DOWN = 1,
        MOVES = {
            38: UP,
            40: DOWN
        };

        $scope.resultType = [
            {id: 'Matching', value: 'true'},
            {id: 'Non-Matching', value: 'false'}
        ];

        $scope.model = {selectedType:'true'};

        $scope.close = function() {
            $scope.filter_test = null;
            $scope.testResult = null;
        };
        $scope.preview = function(Item) {
            $location.search('_id', Item ? Item._id : Item);
        };
        $scope.openView = function(item) {
            $scope.openLightbox(item);
        };
        $scope.openLightbox = function (item) {
            $scope.selected.view = item;
        };
        $scope.closeLightbox = function () {
            $scope.selected.view = null;
        };
        $scope.hideActions = function () {
            return true;
        };

        $scope.$on('$routeUpdate', previewItem);

        function previewItem() {
            $scope.selectedItem = _.find($scope.testResult, {_id: $location.search()._id}) || null;
            if ($scope.selectedItem) {
                $scope.selected.preview = $scope.selectedItem;
            } else {
                $scope.selected.preview = null;
            }
        }
        $scope.handleKeyEvent = function(event) {
            var code = event.keyCode || event.which;
            if (MOVES[code]) {
                event.preventDefault();
                event.stopPropagation();
                move(MOVES[code], event);
            }
        };

        function move(diff, event) {
            var index = _.findIndex($scope.testResult, $scope.selectedItem),
                nextItem,
                nextIndex;

            if (index === -1) {
                nextItem = $scope.testResult[0];
            } else {
                nextIndex = Math.max(0, Math.min($scope.testResult.length - 1, index + diff));
                nextItem = $scope.testResult[nextIndex];
            }
            clickItem($scope.testResult[nextIndex], event);
        }
        function select(item) {
            $scope.selectedItem = item;
            $location.search('_id', item ? item._id : item);
        }

        function clickItem(item, event) {
            select(item);
            if (event) {
                event.preventDefault();
                event.stopPropagation();
                event.stopImmediatePropagation();
            }
        }
        $scope.fetchResults = function() {
            fetchProductionTestResult();
        };
        $scope.$on('triggerTest', function (event, filter) {
            $scope.productionTest = true;
            $scope.testResult = null;
            $scope.selectedfilter = filter._id;
            fetchProductionTestResult();
        });
        var fetchProductionTestResult = function() {
            contentFilters.testContentFilter({
                'filter_id': $scope.selectedfilter,
                'return_matching': $scope.$eval($scope.model.selectedType
            )}).then(
                function(result) {
                    $scope.testResult = result.match_results;
                },
                function(response) {
                    if (angular.isDefined(response.data._issues)) {
                        notify.error(gettext('Error: ' + response.data._issues));
                    } else if (angular.isDefined(response.data._message)) {
                        notify.error(gettext('Error: ' + response.data._message));
                    } else {
                        notify.error(gettext('Error: Failed to fetch production test results.'));
                    }
                }
            );

        };
    }

    /**
     * @memberof superdesk.content_filters
     * @ngdoc controller
     * @name FilterSearchCtrl
     * @description
     *   Controller for the Filter Search tab, found on the Content Filters
     *   settings page.
     */
    FilterSearchController.$inject = ['$scope', 'contentFilters', 'notify'];
    function FilterSearchController($scope, contentFilters, notify) {
        $scope.filterCondition = null;
        $scope.operatorLookup = {};
        $scope.valueLookup = {};
        $scope.valueFieldLookup = {};
        $scope.searchResult = null;
        $scope.contentFiltersLookup = {};

        $scope.isListValue = function() {
            if ($scope.filterCondition != null) {
                return _.contains(['in', 'nin'], $scope.filterCondition.operator) && $scope.valueLookup[$scope.filterCondition.field];
            }
        };

        $scope.hideList = true;

        $scope.handleKey = function(event) {
            if ($scope.filterCondition.values.length > 0) {
                notify.error(gettext('single value is required'));
                event.preventDefault();
                event.stopPropagation();
                return false;
            }
        };
        $scope.resetValues = function() {
            $scope.searchResult = null;
            $scope.filterCondition.values.length = 0;
            $scope.filterCondition.value = null;
        };

        $scope.getFilter = function(filterId) {
            return _.find($scope.contentFilters, {_id: filterId});
        };

        function fetchContentFilters() {
            contentFilters.getAllContentFilters().then(function(_filters) {
                $scope.contentFilters = _filters;
                _.each($scope.contentFilters, function(filter) {
                    $scope.contentFiltersLookup[filter._id] = filter;
                });
            });
        }

        function populateData() {
            return contentFilters.getFilterConditionParameters().then(function(params) {
                $scope.filterConditionParameters = params;
                _.each(params, function(param) {
                    $scope.operatorLookup[param.field] = param.operators;
                    $scope.valueLookup[param.field] = param.values;
                    $scope.valueFieldLookup[param.field] = param.value_field;
                });

                $scope.origFilterCondition = {};
                $scope.filterCondition = _.create($scope.origFilterCondition);
                $scope.filterCondition.values = [];
                setFilterValues();
            });
        }

        function setFilterValues() {
            var values = $scope.filterCondition.value != null ? $scope.filterCondition.value.split(',') : [];
            var all_values = $scope.valueLookup[$scope.filterCondition.field];
            var value_field = $scope.valueFieldLookup[$scope.filterCondition.field];

            _.each(values, function(value) {
                var v = _.find(all_values, function(val) {
                    return val[value_field].toString() === value;
                });

                $scope.filterCondition.values.push(v);
            });
        }

        function getFilterValue() {
            if ($scope.isListValue()) {
                var values = [];
                _.each($scope.filterCondition.values, function(value) {
                    values.push(value[$scope.valueFieldLookup[$scope.filterCondition.field]]);
                });
                return values.join();
            } else {
                return $scope.filterCondition.value;
            }
        }

        $scope.search = function() {
            if (!$scope.loading) {
                $scope.searchResult = null;
                $scope.filterCondition.value = getFilterValue();
                var inputs = {
                    'field': $scope.filterCondition.field,
                    'operator': $scope.filterCondition.operator,
                    'value': $scope.filterCondition.value
                };
                $scope.loading = true;
                contentFilters.getFilterSearchResults(inputs).then(function(result) {
                    $scope.searchResult = result;
                    if (result.length === 0) {
                        notify.error(gettext('no results found'));
                    }
                    $scope.filterCondition.value = null;
                })
                ['finally'](function() {
                    $scope.loading = false;
                });
            }
        };

        populateData().then(function() {
            fetchContentFilters();
        });
    }

    // XXX: For some reason, loading the superdesk.content_filters module in
    // tests fails to load due to "Unknown provider: superdeskProvider" error.
    // This happens if any taste case uses the inject() function.
    // Seems like something needs to be fixed in config, but for now loading
    // superdesk.publish module does the trick (FWIW, it's the module that
    // contained the original code for the content_filters module).
    var module = angular.module('superdesk.content_filters', ['superdesk.publish']);

    module.config(['superdeskProvider', function (superdesk) {
            var templateUrl = 'scripts/superdesk-content-filters/' +
                              'views/settings.html';

            superdesk.activity('/settings/content-filters', {
                    label: gettext('Content Filters'),
                    controller: ContentFiltersConfigController,
                    controllerAs: 'ctrl',
                    templateUrl: templateUrl,
                    category: superdesk.MENU_SETTINGS,
                    priority: -800,
                    privileges: {dictionaries: 1}
                });
        }])
        .service('contentFilters', ContentFiltersService)
        .controller('ContentFiltersConfigCtrl', ContentFiltersConfigController)
        .controller('FilterConditionsCtrl', FilterConditionsController)
        .controller('ManageContentFiltersCtrl', ManageContentFiltersController)
        .controller('ProductionTestCtrl', ProductionTestController)
        .controller('FilterSearchCtrl', FilterSearchController)
        .directive('sdManageFiltersTab', manageFiltersTabDirective);
})();
