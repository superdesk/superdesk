define([
    'angular',
    'require',
    './list-view-directive',
    './search-param-directive',
    './searchbar-directive',
    './list-item-directive'
], function(angular, require) {
    'use strict';

    var mod = angular.module('superdesk.list', []);
    mod.directive('sdListView', require('./list-view-directive'));
    mod.directive('sdSearchParam', require('./search-param-directive'));
    mod.directive('sdSearchbar', require('./searchbar-directive'));
    mod.directive('sdListItem', require('./list-item-directive'));

    /**
     * sdPagination inserts pagination controls for a given data set.
     *
     * Usage:
     * <div sd-pagination data-items="users" data-limit="maxResults"></div>
     *
     * Params:
     * @items {object} Item container as received from server, with _items and _meta.
     * @limit {number} Number of items per page.
     */
    mod.directive('sdPagination', ['$location', function($location) {
        return {
            templateUrl: require.toUrl('./views/sdPagination.html'),
            scope: {
                items: '=',
                limit: '='
            },
            link: function(scope, element, attrs) {

                scope.$watch('items', function(items) {
                    if (items && items._meta) {
                        scope.total = items._meta.total;
                        scope.page = $location.search().page || 1;
                        scope.lastPage = scope.limit ? Math.ceil(scope.total / scope.limit) : scope.page;
                        scope.from = (scope.page - 1) * scope.limit + 1;
                        scope.to = Math.min(scope.total, scope.from + scope.limit - 1);
                    }
                });

                /**
                 * Set page
                 *
                 * @param {integer} page
                 */
                scope.setPage = function(page) {
                    $location.search('page', page > 1 ? page : null);
                };
            }
        };
    }]);

    return mod;
});
