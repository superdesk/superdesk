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
            var getParameters = function(url) {
                var parameters = {};
                var parts = url.split('?');
                parts = parts[1].split('&');
                _.forEach(parts, function(part) {
                    var item = part.split('=');
                    parameters[item[0]] = item[1];
                });
                return parameters;
            };

            return {
                scope: {
                    data: '=sdDataModel',
                    state: '=sdStateHandler'
                },
                templateUrl: 'scripts/superdesk/views/sdPagination.html',
                link: function($scope, element, attrs) {
                    $scope.pageTotal = $scope.page;
                    if ($scope.data.links.last !== undefined) {
                        $scope.pageTotal = getParameters($scope.data.links.last).page;
                    }
                }
            };
        });
});
