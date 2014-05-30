define([
    'angular',
    'require',
    './pagination-directive',
    './list-view-directive',
    './search-param-directive',
    './searchbar-directive',
    './list-item-directive'
], function(angular, require) {
    'use strict';

    var mod = angular.module('superdesk.list', []);
    mod.directive('sdPagination', require('./pagination-directive'));
    mod.directive('sdListView', require('./list-view-directive'));
    mod.directive('sdSearchParam', require('./search-param-directive'));
    mod.directive('sdSearchbar', require('./searchbar-directive'));
    mod.directive('sdListItem', require('./list-item-directive'));
    return mod;
});
