define([
    'angular'
], function(angular) {
    'use strict';

    return angular.module('superdesk.directives.searchList', ['superdesk.asset'])
        /**
         * SearchList directive displays a searchable paginated list of items from
         * given endpoint, allows selecting multiple items.
         *
         * Usage:
         * <div sd-search-list
         * data-endpoint="subscribers"
         * data-page-size="5"
         * data-label-key="name"
         * data-search-key="name"
         * data-criteria="criteria"
         * data-max-selected-items="1"
         * data-disabled-items="disabledItems"
         * data-selected-items="selectedItems"
         * data-selected-items-helper-template="helperTemplate.html"
         * data-selected-items-helper-data="data"
         * ></div>
         *
         * Params:
         * @scope {String} endpoint - api endpoint to send queries
         * @scope {Integer} pageSize - number of items per page
         * @scope {String} labelKey - object key to display items by
         * @scope {String} searchKey - object key to search keyword in
         * @scope {Object} criteria - base criteria object to use in queries
         * @scope {Integer} maxSelectedItems - maximum number of items to select
         * @scope {Array} disabledItems - items that will be disabled
         * @scope {Array} selectedItems - target to populate with selected items
         * @scope {String} selectedItemsHelperTemplate - additional template to
         *      display for each selected item
         * @scope {Object} selectedItemsHelperData - additional data to use in
         *      helper template, which can be accessed by data variable
         *
         */
        .directive('sdSearchList', ['asset', 'api', function(asset, api) {
            var defaults = {
                pageSize: 25
            };
            return {
                scope: {
                    endpoint: '@',
                    pageSize: '@',
                    labelKey: '@',
                    searchKey: '@',
                    maxSelectedItems: '=',
                    criteria: '=',
                    disabledItems: '=',
                    selectedItems: '=',
                    selectedItemsHelperTemplate: '=',
                    selectedItemsHelperData: '='
                },
                templateUrl: asset.templateUrl('superdesk/views/sdSearchList.html'),
                link: function(scope, element, attrs) {
                    scope.open = false;
                    scope.page = 1;
                    scope.maxPage = 0;
                    scope.items = null;
                    scope.keyword = null;

                    scope.editable = true;
                    if (scope.$parent._editable != null) {
                        scope.editable = scope.$parent._editable;
                    }

                    var _update = function() {
                        var criteria = scope.criteria || {};
                        if (scope.keyword && scope.searchKey) {
                            var search = {};
                            search[scope.searchKey] = {'$regex': scope.keyword, '$options': '-i'};
                            criteria.where = JSON.stringify({'$or': [search]});
                        }
                        api[scope.endpoint].query(_.assign({}, criteria, {
                            max_results: scope.pageSize,
                            page: scope.page
                        }))
                        .then(function(result) {
                            var pageSize = scope.pageSize || defaults.pageSize;
                            scope.maxPage = Math.ceil(result._meta.total / pageSize) || 0;
                            scope.items = result._items;
                        });
                    };
                    var update = _.debounce(_update, 500);
                    scope.$watch('keyword', function() {
                        scope.page = 1;
                        update();
                    });
                    scope.$watch('page', update);

                    scope.selectItem = function(item) {
                        scope.selectedItems = scope.selectedItems || [];
                        scope.selectedItems.push(item);
                        scope.selectedItems = _.uniq(scope.selectedItems);
                        if (scope.maxSelectedItems === 1) {
                            scope.open = false;
                        }
                    };

                    scope.unselectItem = function(item) {
                        _.remove(scope.selectedItems, function(i) {
                            return i._id === item._id;
                        });
                    };

                    scope.isSelected = function(item) {
                        return scope.selectedItems ? _.findIndex(scope.selectedItems, function(i) {
                            return i._id === item._id;
                        }) !== -1 : false;
                    };

                    scope.isDisabled = function(item) {
                        return scope.disabledItems ? _.findIndex(scope.disabledItems, function(i) {
                            return i._id === item._id;
                        }) !== -1 : false;
                    };
                }
            };
        }])
        /**
         * SearchListSingle directive is a proxy directive for SearchList,
         * limiting it to a single item for ease of use.
         *
         * Usage:
         * <div sd-search-list
         * data-endpoint="subscribers"
         * data-page-size="5"
         * data-label-key="name"
         * data-search-key="name"
         * data-criteria="criteria"
         * data-disabled-items="disabledItems"
         * data-selected-item="selectedItem"
         * ></div>
         *
         * Params:
         * @scope {String} endpoint - api endpoint to send queries
         * @scope {Integer} pageSize - number of items per page
         * @scope {String} labelKey - object key to display items by
         * @scope {String} searchKey - object key to search keyword in
         * @scope {Object} criteria - base criteria object to use in queries
         * @scope {Integer} maxSelectedItems - maximum number of items to select
         * @scope {Array} disabledItems - items that will be disabled
         * @scope {Object} selectedItem - target to populate with selected item
         *
         */
        .directive('sdSearchListSingle', ['asset', function(asset) {
            return {
                scope: {
                    endpoint: '@',
                    pageSize: '@',
                    labelKey: '@',
                    searchKey: '@',
                    criteria: '=',
                    disabledItems: '=',
                    selectedItem: '='
                },
                templateUrl: asset.templateUrl('superdesk/views/sdSearchListSingle.html'),
                link: function(scope, element, attrs) {
                    scope.selectedItems = [];

                    scope.$watch('selectedItems', function() {
                        if (Array.isArray(scope.selectedItems)) {
                            scope.selectedItem = _.last(scope.selectedItems);
                        }
                    });
                }
            };
        }]);
});
