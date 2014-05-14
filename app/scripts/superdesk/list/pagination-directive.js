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

        function getTotalItems(data) {
            if (data && data._links && data._links.last != null) {
                var parts = data._links.last.href.split('?')[1].split('&');
                var parameters = {};
                _.forEach(parts, function(part) {
                    var item = part.split('=');
                    parameters[item[0]] = item[1];
                });
                if (parameters.page !== undefined) {
                    return parameters.page * 25; //hardcoded
                }
            }
            return undefined;
        }

        return {
            templateUrl: require.toUrl('./views/sdPagination.html'),
            scope: {
                items: '=',
                limit: '='
            },

            link: function(scope, element, attrs) {

                var params = {};
                scope.$watchCollection(function() {
                    params.page = $location.search().page || 0;
                    params.limit = scope.limit;
                    params.items = scope.items;
                    return params;
                }, function() {
                    scope.total = getTotalItems(params.items);
                    scope.page = Math.max(0, params.page);
                    scope.lastPage = params.limit ? Math.ceil(scope.total / params.limit) - 1 : 0;
                    scope.from = scope.page * params.limit + 1;
                    scope.to = Math.min(scope.total, scope.from + params.limit - 1);
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
