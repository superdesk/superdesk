define([
    'jquery',
    'angular'
], function($, angular) {
    'use strict';

    angular.module('superdesk.directives')
        /**
         * sdSort inserts sort links based on current sort field and direction.
         *
         * Usage:
         * <a href=""
                sd-sort
                data-sort-field-text="{{ 'Name'|translate }}"
                data-sort-field-name="display_name"
                sd-sort-field-model="routeParams.sortField"
                sd-sort-direction-model="routeParams.sortDirection"
            ></a>
         * 
         * Params:
         * @param {string} sortFieldText - user friendly text for sort field
         * @param {string} sortFieldName - field name for sort field
         * @param {string} sdSortFieldModel - model for sort field
         * @param {string} sdSortDirectionModel - model for sort direction
         */
        .directive('sdSort', function() {
            return {
                scope: {
                    sortField: '=sdSortFieldModel',
                    sortDirection: '=sdSortDirectionModel'
                },
                templateUrl: 'scripts/superdesk/views/sdSort.html',
                link: function($scope, element, attrs) {
                    $scope.sortFieldText = attrs.sortFieldText;
                    $scope.sortFieldName = attrs.sortFieldName;

                    element.on('click', function() {
                        $scope.$apply(function() {
                            if ($scope.sortField === $scope.sortFieldName) {
                                if ($scope.sortDirection === 'asc') {
                                    $scope.sortDirection = 'desc';
                                } else {
                                    $scope.sortDirection = 'asc';
                                }
                            } else {
                                $scope.sortField = $scope.sortFieldName;
                                $scope.sortDirection = 'asc';
                            }
                        });
                    });
                }
            };
        });
});
