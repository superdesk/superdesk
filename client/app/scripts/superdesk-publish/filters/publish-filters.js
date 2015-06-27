(function() {

'use strict';

FilterConditionsService.$inject = ['api'];
function FilterConditionsService(api) {
    this.get = function() {
        return api.query('filter_conditions')
            .then(angular.bind(this, function(filter_conditions) {
                this.filter_conditions = filter_conditions._items;
                return this.filter_conditions;
            }));
    };

    this.getFilterConditionParameters = function() {
        return api.query('filter_conditions/parameters')
            .then(angular.bind(this, function(params) {
                this.filter_condition_parameters = params._items;
                return this.filter_condition_parameters;
            }));
    };

    this.save = function(orig, diff) {
        return api.save('filter_conditions', orig, diff);
    };

    this.remove = function(item) {
        return api.remove(item);
    };
}

FilterConditionsController.$inject = ['$scope', 'filterConditions', 'notify', 'modal'];
function FilterConditionsController($scope, filterConditions, notify, modal) {
    $scope.filterConditions = null;
    $scope.filterCondition = null;
    $scope.origFilterCondition = null;
    $scope.filterConditionParameters = null;
    $scope.operatorLookup = {};
    $scope.valueLookup = {};

    $scope.edit = function(fc) {
        $scope.origFilterCondition = fc || {};
        $scope.filterCondition = _.create($scope.origFilterCondition);
        $scope.filterCondition.values = {};

        filterConditions.getFilterConditionParameters().then(function(params) {
            $scope.filterConditionParameters = params;
            _.each(params, function(param) {
                $scope.operatorLookup[param.field] = param.operators;
                $scope.valueLookup[param.field] = param.values;
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
        filterConditions.save($scope.origFilterCondition, $scope.filterCondition)
            .then(
                function() {
                    notify.success(gettext('Filter condition saved.'));
                    $scope.cancel();
                },
                function(response) {
                    if (angular.isDefined(response.data._issues)) {
                        notify.error(gettext('Error: ' + response.data._issues));
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
            return filterConditions.remove(filterCondition);
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
            _.each($scope.filterCondition.values, function(value, key) {
                if (value.selected) {
                    values.push(key);
                }
            });
            return values.join();
        } else {
            return $scope.filterCondition.value;
        }
    };

    var setFilterValues = function() {
        if ($scope.isListValue()) {
            var values = $scope.filterCondition.value.split(',');
            _.each(values, function(value) {
                $scope.filterCondition.values[value] = {'selected': true};
            });
        }
    };

    var fetchFilterConditions = function() {
        filterConditions.get().then(function(filters) {
            $scope.filterConditions = filters;
        });
    };

    fetchFilterConditions();

}

PublishFiltersController.$inject = ['$scope', 'filterConditions', 'api', 'notify', 'modal'];
function PublishFiltersController($scope, filterConditions, api, notify, modal) {
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
        $scope.publishFilter.publish_filter = _.cloneDeep($scope.origPublishFilter.publish_filter)
        initPublishFilter();
        $scope.previewPublishFilter();
        console.log('Edit $scope.publishFilter:', $scope.publishFilter);
    };

    $scope.cancel = function() {
        $scope.previewPublishFilter();
        $scope.origPublishFilter = null;
        $scope.publishFilter = null;
    };

    $scope.save = function() {
        var stringJSON = JSON.stringify($scope.publishFilter.publish_filter);
        api.save('publish_filters', $scope.origPublishFilter, $scope.publishFilter)
            .then(
                function() {
                    notify.success(gettext('Publish filter saved.'));
                    $scope.cancel();
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
            ).then(fetchPublishFilters);
    };

    $scope.remove = function(pf) {
        modal.confirm(gettext('Are you sure you want to delete publish filter?'))
        .then(function() {
            return api.remove(pf);
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
    }

    $scope.removeStatement = function(index) {
        $scope.publishFilter.publish_filter.splice(index, 1);
    }

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


    $scope.previewPublishFilter = function() {
         $scope.preview = '';
         var previews = [];
        _.each($scope.publishFilter.publish_filter, function(filterRow) {
            var statementPreviews = [];
            if ('fc' in filterRow.expression) {
                _.each(filterRow.expression.fc, function(filterId) {
                    var f = $scope.filterConditionLookup[filterId];
                    statementPreviews.push('(' + f.field + ' ' + f.operator + ' "' + f.value + '")');
                });
            } else {
                $scope.preview += ' TIM-TAM';
            }
            
            if (statementPreviews.length > 0) {
                previews.push('[' + statementPreviews.join(' AND ') + ']');
            }
        });

        if (previews.length > 0) {
            $scope.preview = previews.join(' OR ');
        }

        console.log('Preview $scope.publishFilter:', $scope.publishFilter);
    }

    var initPublishFilter = function() {
        if (!$scope.publishFilter.publish_filter || $scope.publishFilter.publish_filter.length == 0)
        {
            // _.each($scope.publishFilter.publish_filter, function(filterExpression) {
            //     _.each(filterExpression, function(filterRow, i) {
            //         if ('fc' in filterRow) {
            //             var fc = [];
            //             _.each(filterRow.fc, function(filter) {
            //                 fc.push({'name': $scope.filterConditionLookup[filter]});
            //             });
            //             row.expression = {'fc': fc};
            //         } else {
            //             var pf = [];
            //             _.each(filterRow.pf, function(filter) {
            //                 pf.push({'name': $scope.publishFiltersLookup[filter]});
            //             });
            //             row.expression = {'pf': pf};
            //         }
            //     });
                
            //     filters.push(row);
            //     var row = {'expression': {}};
            // });
            $scope.publishFilter.publish_filter = [{'expression': {}}];
        }
    };


    var fetchFilterConditions = function() {
        filterConditions.get().then(function(filters) {
            $scope.filterConditions = filters;
            _.each(filters, function(filter) {
                $scope.filterConditionLookup[filter._id] = filter;
            });
        });
    };

    var fetchPublishFilters = function() {
        api.query('publish_filters').then(function(filters) {
            $scope.publishFilters = filters._items;
            _.each(filters, function(filter) {
                $scope.publishFiltersLookup[filter._id] = filter;
            });
        });
    };

    fetchFilterConditions();
    fetchPublishFilters();
}

angular.module('superdesk.publish.filters', [])
    .service('filterConditions', FilterConditionsService)
    .controller('FilterConditionsController', FilterConditionsController)
    .controller('PublishFiltersController', PublishFiltersController);

})();
