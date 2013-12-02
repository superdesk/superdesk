define([
    'jquery',
    'angular'
], function($, angular) {
    'use strict';

    angular.module('superdesk.directives')
        /**
         * sdUserPermissions checks if user has specified permissions and assigns
         * scope.permitted which can be used to disable/enable certain features.
         *
         * Usage:
         * <div sd-user-permissions data-required="required" ng-show="permitted"></div>
         * 
         * Params:
         * @param {Object} dataRequired - required permissions in {resource: [method, ...], ...} format.
         */
        .directive('sdUserPermissions', ['userPermissions', function(userPermissions) {
            return {
                scope: {required: '='},
                link: function(scope, element, attrs) {
                    scope.permitted = false;
                    if (scope.required !== undefined && userPermissions.check(scope.required) === true) {
                        scope.permitted = true;
                    }
                }
            };
        }]);
});
