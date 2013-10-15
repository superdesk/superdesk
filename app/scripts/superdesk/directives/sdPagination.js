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
         * <div sd-pagination sd-data-model="list" sd-page-model="page"></div>
         * 
         * Params:
         * @param {ResourceList} sdDataModel - model for data
         * @param {number} sdPageModel - model for current page
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
                    page: '=sdPageModel'
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
