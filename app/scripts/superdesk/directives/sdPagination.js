define([
    'jquery',
    'angular'
], function($, angular) {
    'use strict';

    angular.module('superdesk.directives')
        /**
         * sdPagination inserts pagination controls for a given data set.
         *
         * Usage:
         * <div sd-pagination sd-data-model="list" sd-state-handler="state"></div>
         * 
         * Params:
         * @param {Array} sdDataModel - model for data
         * @param {Object} sdStateHandler - handler for application state
         */
        .directive('sdPagination', function() {
            var getTotalPages = function(data) {
                if (data._links.last !== undefined) {
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
                return 1;
            };

            return {
                scope: {
                    data: '=sdDataModel',
                    state: '=sdStateHandler'
                },
                templateUrl: 'scripts/superdesk/views/sdPagination.html',
                link: function($scope, element, attrs) {
                    $scope.currentPage = $scope.state.get('page');
                    $scope.totalPages = _.max([getTotalPages($scope.data), $scope.currentPage]);
                }
            };
        });
});
