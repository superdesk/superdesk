define([
    'angular',
    'require',
    './pagination-directive',
    './list-view-directive',
    './search-param-directive',
    './searchbar-directive'
], function(angular, require) {
    'use strict';

    return angular.module('superdesk.list', [])
        .directive('sdPagination', require('./pagination-directive'))
        .directive('sdListView', require('./list-view-directive'))
        .directive('sdSearchParam', require('./search-param-directive'))
        .directive('sdSearchbar', require('./searchbar-directive'));
});
