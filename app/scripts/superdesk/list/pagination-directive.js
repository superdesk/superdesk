define(['require'], function(require) {
    'use strict';

    /**
     * sdPagination inserts pagination controls for a given data set.
     *
     * Usage:
     * <div sd-pagination data-items="users" data-limit="maxResults"></div>
     *
     * Params:
     * @data-items {object} Item container as received from server, with _items and _links.
     * @data-limit {number} Maximum number of items per page.
     */
    return ['$location', function($location) {

        function getPage(url) {
            return parseInt(/page=([0-9]+)/.exec(url)[1], 10) + 1;
        }

        function getTotal(data, limit) {
            var total = 0;
            if (data._links) {
                if (data._links.last) {
                    // (any but last) of many pages
                    total = getPage(data._links.last.href) * limit;
                } else if (data._links.prev) {
                    // last of many pages
                    total = (getPage(data._links.prev.href) * limit) + data._items.length;
                } else {
                    // one page
                    total = data._items.length;
                }
            }
            return total;
        }

        return {
            templateUrl: require.toUrl('./views/sdPagination.html'),
            scope: {
                items: '=',
                limit: '='
            },

            link: function(scope, element, attrs) {

                scope.$watchCollection('items', function() {
                    if (scope.items) {
                        scope.total = getTotal(scope.items, scope.limit);
                        scope.page = Math.max(0, $location.search().page || 0);
                        scope.lastPage = scope.limit ? Math.ceil(scope.total / scope.limit) - 1 : 0;
                        scope.from = scope.page * scope.limit + 1;
                        scope.to = Math.min(scope.total, scope.from + scope.limit - 1);
                        scope.approx = !!(scope.items._links && scope.items._links.last);
                    }
                });

                /**
                 * Set page
                 *
                 * @param {integer} page
                 */
                scope.setPage = function(page) {
                    $location.search('page', page ? page : null);
                };
            }
        };
    }];
});
