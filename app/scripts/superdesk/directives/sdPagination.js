define([
    'angular'
], function(angular) {
    'use strict';

    angular.module('superdesk.directives')
        /**
         * sdPagination inserts pagination controls for a given data set.
         *
         * Usage:
         * <div sd-pagination data-cursor="list"></div>
         *
         * Params:
         * @data {Object} cursor
         */
        .directive('sdPagination', ['$location', function($location) {
            return {
                scope: {cursor: '='},
                templateUrl: 'scripts/superdesk/views/sdPagination.html',
                link: function(scope, element, attrs) {
                    scope.$watch(function() {
                        return $location.search().page || 0;
                    }, function(page) {
                        scope.page = page;
                    });

                    scope.$watch('cursor', function(cursor) {
                        var total = cursor && cursor.total,
                            limit = cursor && cursor.maxResults;

                        if (limit) {
                            scope.lastPage = Math.ceil(total / limit) - 1;
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
        }]);
});
