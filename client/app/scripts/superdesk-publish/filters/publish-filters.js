(function() {

'use strict';

FiltersService.$inject = ['api'];
function FiltersService(api) {

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

    this.getAllPublishFilters = function(page, items) {
        return _getAll('publish_filters', page, items);
    };

    this.savePublishFilter = function(orig, diff) {
        return api.save('publish_filters', orig, diff);
    };

    this.testPublishFilter = function(diff) {
        return api.save('publish_filter_tests', {}, diff);
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

FilterConditionsController.$inject = ['$scope', 'filters', 'notify', 'modal'];
function FilterConditionsController($scope, filters, notify, modal) {
    $scope.filterConditions = null;
    $scope.filterCondition = null;
    $scope.origFilterCondition = null;
    $scope.filterConditionParameters = null;
    $scope.operatorLookup = {};
    $scope.valueLookup = {};
    $scope.valueFieldLookup = {};

    $scope.edit = function(fc) {
        $scope.origFilterCondition = fc || {};
        $scope.filterCondition = _.create($scope.origFilterCondition);
        $scope.filterCondition.values = [];

        filters.getFilterConditionParameters().then(function(params) {
            $scope.filterConditionParameters = params;
            _.each(params, function(param) {
                $scope.operatorLookup[param.field] = param.operators;
                $scope.valueLookup[param.field] = param.values;
                $scope.valueFieldLookup[param.field] = param.value_field;
            });
        });

        setFilterValues();
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
        filters.saveFilterCondition($scope.origFilterCondition, $scope.filterCondition)
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
            return filters.remove(filterCondition);
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
                    return val[value_field] === value;
                });

                $scope.filterCondition.values.push(v);
            });
        }
    };

    var fetchFilterConditions = function() {
        filters.getAllFilterConditions().then(function(f) {
            $scope.filterConditions = f;
        });
    };

    fetchFilterConditions();

}

PublishFiltersController.$inject = ['$scope', 'filters', 'notify', 'modal'];
function PublishFiltersController($scope, filters, notify, modal) {
    $scope.filterConditions = null;
    $scope.publishFilters = null;
    $scope.publishFilter = null;
    $scope.origPublishFilter = null;
    $scope.preview = null;
    $scope.filterConditionLookup = {};
    $scope.publishFiltersLookup = {};

    $scope.edit = function(pf) {
        $scope.origPublishFilter = pf || {};
        $scope.publishFilter = _.create($scope.origPublishFilter);
        $scope.publishFilter.name =  $scope.origPublishFilter.name;
        $scope.publishFilter.publish_filter = _.cloneDeep($scope.origPublishFilter.publish_filter);
        initPublishFilter();
        $scope.previewPublishFilter();
    };

    $scope.cancel = function() {
        $scope.previewPublishFilter();
        $scope.origPublishFilter = null;
        $scope.publishFilter = null;
        $scope.test.test_result = null;
        $scope.test.article_id = null;
    };

    $scope.save = function() {
        delete $scope.publishFilter.article_id;
        filters.savePublishFilter($scope.origPublishFilter, $scope.publishFilter)
            .then(
                function() {
                    notify.success(gettext('Publish filter saved.'));
                    $scope.cancel();
                },
                function(response) {
                    if (angular.isDefined(response.data._issues['validator exception'])) {
                        notify.error(gettext('Error: ' + response.data._issues['validator exception']));
                    } else if (angular.isDefined(response.data._issues)) {
                        if (response.data._issues.name && response.data._issues.name.unique) {
                            notify.error(gettext('Error: ' + gettext('Name needs to be unique')));
                        } else {
                            notify.error(gettext('Error: ' + JSON.stringify(response.data._issues)));
                        }
                    } else if (angular.isDefined(response.data._message)) {
                        notify.error(gettext('Error: ' + response.data._message));
                    } else if (angular.isDefined(response.status === 500)) {
                        notify.error(gettext('Error: Internal error in Filter testing'));
                    } else {
                        notify.error(gettext('Error: Failed to test publish filter.'));
                    }
                }
            ).then(fetchPublishFilters);
    };

    $scope.remove = function(pf) {
        modal.confirm(gettext('Are you sure you want to delete publish filter?'))
        .then(function() {
            return filters.remove(pf);
        })
        .then(function(result) {
            _.remove($scope.publishFilters, pf);
        }, function(response) {
            if (angular.isDefined(response.data._message)) {
                notify.error(gettext('Error: ' + response.data._message));
            } else {
                notify.error(gettext('There is an error. Publish filter cannot be deleted.'));
            }
        });
    };

    $scope.addStatement = function() {
        $scope.publishFilter.publish_filter.push({'expression': {}});
    };

    $scope.removeStatement = function(index) {
        $scope.publishFilter.publish_filter.splice(index, 1);
        $scope.previewPublishFilter();
    };

    $scope.addFilter = function(filterRow, filterType) {
        if (!(filterType in filterRow.expression)) {
            filterRow.expression[filterType] = [];
        }

        if (filterRow.selected && !_.includes(filterRow.expression[filterType], filterRow.selected)) {
            filterRow.expression[filterType].push(filterRow.selected);
            delete filterRow.selected;
            $scope.previewPublishFilter();
        }
    };

    $scope.removeFilter = function(filterRow, filterId, filterType) {
        filterRow.expression[filterType] = _.without(filterRow.expression[filterType], filterId);
        $scope.previewPublishFilter();
    };

    $scope.test = function() {
        if (!$scope.test.article_id) {
            notify.error(gettext('Please provide an article id'));
            return;
        }

        filters.testPublishFilter({'filter': $scope.publishFilter, 'article_id': $scope.test.article_id})
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
                        notify.error(gettext('Error: Failed to save publish filter.'));
                    }
                }
            );
    };

    $scope.previewPublishFilter = function() {
        $scope.preview = parsePublishFilter($scope.publishFilter.publish_filter);
    };

    var parsePublishFilter = function(publishFilter) {
        var previews = [];
        _.each(publishFilter, function(filterRow) {
            var statementPreviews = [];

            if ('pf' in filterRow.expression) {
                _.each(filterRow.expression.pf, function(filterId) {
                    var f = $scope.publishFiltersLookup[filterId];
                    statementPreviews.push(parsePublishFilter(f.publish_filter));
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

    var initPublishFilter = function() {
        if (!$scope.publishFilter.publish_filter || $scope.publishFilter.publish_filter.length === 0)
        {
            $scope.publishFilter.publish_filter = [{'expression': {}}];
        }
    };

    var fetchFilterConditions = function() {
        filters.getAllFilterConditions().then(function(_filters) {
            $scope.filterConditions = _filters;
            _.each(_filters, function(filter) {
                $scope.filterConditionLookup[filter._id] = filter;
            });
        });
    };

    var fetchPublishFilters = function() {
        filters.getAllPublishFilters().then(function(_filters) {
            $scope.publishFilters = _filters;
            _.each($scope.publishFilters, function(filter) {
                $scope.publishFiltersLookup[filter._id] = filter;
            });
        });
    };

    fetchFilterConditions();
    fetchPublishFilters();
}

angular.module('superdesk.publish.filters', [])
    .service('filters', FiltersService)
    .controller('FilterConditionsController', FilterConditionsController)
    .controller('PublishFiltersController', PublishFiltersController);
})();
