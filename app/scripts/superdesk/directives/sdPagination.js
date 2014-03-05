define([
    'angular'
], function(angular) {
    'use strict';

    angular.module('superdesk.directives')
        /**
         * sdPagination inserts pagination controls for a given data set.
         *
         * Usage:
         * <div sd-pagination data-model="list"></div>
         *
         * Params:
         * @scope {Object} dataModel - model for data
         */
        .directive('sdPagination', ['locationParams', function(locationParams) {

            function getTotalPages(data) {
                if (data && data._links && data._links.last != null) {
                    var parts = data._links.last.href.split('?')[1].split('&');
                    var parameters = {};
                    _.forEach(parts, function(part) {
                        var item = part.split('=');
                        parameters[item[0]] = item[1];
                    });
                    if (parameters.page !== undefined) {
                        return parameters.page;
                    }
                }
                return undefined;
            }

            return {
                scope: {adapter: '='},
                templateUrl: 'scripts/superdesk/views/sdPagination.html',
                link: function(scope, element, attrs) {

                    scope.$watch('adapter._links', function(links) {
                        if (links) {
                            scope.page = scope.adapter.page();
                            scope.totalPages = getTotalPages(scope.adapter || scope.page);
                            scope.links = links;
                        } else {
                            scope.page = scope.totalPages = 0;
                            scope.links = {};
                        }
                    });

                    scope.$watch('page', function(page) {
                        //scope.adapter.page(page);
                    });
                }
            };
        }]);
});
