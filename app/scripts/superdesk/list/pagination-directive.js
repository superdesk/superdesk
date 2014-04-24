define(['require'], function(require) {
    'use strict';

    /**
     * sdPagination inserts pagination controls for a given data set.
     *
     * Usage:
     * <div sd-pagination data-cursor="list"></div>
     *
     * Params:
     * @data {Object} cursor
     */
    return ['$location', function($location) {
        return {
            templateUrl: require.toUrl('./views/sdPagination.html'),
            scope: {
                total: '=',
                limit: '='
            },
            link: function(scope, element, attrs) {

                var params = {};
                scope.$watchCollection(function() {
                    params.page = $location.search().page || 0;
                    params.limit = scope.limit;
                    params.total = scope.total;
                    return params;
                }, function() {
                    scope.page = Math.max(0, params.page);
                    scope.lastPage = params.limit ? Math.ceil(params.total / params.limit) - 1 : 0;
                    scope.from = scope.page * params.limit + 1;
                    scope.to = Math.min(params.total, scope.from + params.limit - 1);
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
