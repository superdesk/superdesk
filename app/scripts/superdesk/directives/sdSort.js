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
                data-label="{{ 'Name'|translate }}"
                data-field="display_name"
            ></a>
         * 
         * Params:
         * @param {string} sortFieldText - user friendly text for sort field
         * @param {string} sortFieldName - field name for sort field
         * @param {string} sdSortFieldKey - state key for sort field
         * @param {string} sdSortDirectionKey - state key for sort direction
         * @param {Object} sdStateHandler - handler for application state
         */
        .directive('sdSort', function(locationParams) {
            return {
                scope: {
                    label: '@',
                    field: '@'
                },
                templateUrl: 'scripts/superdesk/views/sdSort.html',
                link: function(scope, element, attrs) {
                    scope.sort = locationParams.get('sort');
                    element.click(function() {
                        scope.$apply(function() {
                            if (scope.field === scope.sort[0]) {
                                locationParams.set('sort', [scope.field, scope.sort[1] === 'asc' ? 'desc' : 'asc']);
                            } else {
                                locationParams.set('sort', [scope.field, 'asc']);
                            }
                        });
                    });
                }
            };
        });
});
