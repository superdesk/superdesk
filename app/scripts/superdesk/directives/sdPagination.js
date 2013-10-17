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
        .directive('sdPagination', function($location) {

            function getTotalPages(data) {
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
            }

            return {
                priority: 2000,
                require: 'ngModel',
                templateUrl: 'scripts/superdesk/views/sdPagination.html',
                link: function($scope, element, attrs, ngModel) {
                    ngModel.$render = function() {
                        $scope.currentPage = ngModel.$viewValue._criteria.page || 1;
                        $scope.totalPages = _.max([getTotalPages(ngModel.$viewValue), $scope.currentPage]);
                        $scope.links = ngModel.$viewValue._links;
                        $scope.state = ngModel.$viewValue._criteria;
                    };

                    $scope.get = function(key) {
                        return $scope.state[key];
                    };

                    $scope.set = function(key, val) {
                        $location.search(key, $scope.state.set(key, val));
                    };
                }
            };
        });
});
