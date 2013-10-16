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
                data-sort-field-key="sortField"
                data-sort-direction-key="sortDirection"
                sd-state-handler="state"
            ></a>
         * 
         * Params:
         * @param {string} sortFieldText - user friendly text for sort field
         * @param {string} sortFieldName - field name for sort field
         * @param {string} sdSortFieldKey - state key for sort field
         * @param {string} sdSortDirectionKey - state key for sort direction
         * @param {Object} sdStateHandler - handler for application state
         */
        .directive('sdSort', function() {
            var sortFieldKey = 'sortField';
            var sortDirectionKey = 'sortDirection';

            return {
                scope: {
                    state: '=sdStateHandler'
                },
                templateUrl: 'scripts/superdesk/views/sdSort.html',
                link: function($scope, element, attrs) {
                    $scope.sortFieldText = attrs.sortFieldText;
                    $scope.sortFieldName = attrs.sortFieldName;
                    if (attrs.sortFieldKey !== '' && attrs.sortFieldKey !== undefined) {
                        sortFieldKey = attrs.sortFieldKey;
                    }
                    if (attrs.sortDirectionKey !== '' && attrs.sortDirectionKey !== undefined) {
                        sortDirectionKey = attrs.sortDirectionKey;
                    }
                    $scope.sortFieldKey = sortFieldKey;
                    $scope.sortDirectionKey = sortDirectionKey;

                    element.on('click', function() {
                        $scope.$apply(function() {
                            if ($scope.state.get(sortFieldKey) === $scope.sortFieldName) {
                                if ($scope.state.get(sortDirectionKey) === 'asc') {
                                    $scope.state.set(sortDirectionKey, 'desc');
                                } else {
                                    $scope.state.set(sortDirectionKey, 'asc');
                                }
                            } else {
                                $scope.state.set(sortFieldKey, $scope.sortFieldName);
                                $scope.state.set(sortDirectionKey, 'asc');
                            }
                        });
                    });
                }
            };
        });
});
