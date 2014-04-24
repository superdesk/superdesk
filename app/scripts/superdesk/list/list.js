define([
    'angular',
    './pagination-directive',
    './list-view-directive',
    './search-param-directive'
], function(angular, PaginationDirective, ListViewDirective, SearchParamDirective) {
    'use strict';

    return angular.module('superdesk.list', [])
        .directive('sdPagination', PaginationDirective)
        .directive('sdListView', ListViewDirective)
        .directive('sdSearchParam', SearchParamDirective);
});
