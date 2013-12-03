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
         * Checking for a user:
         * <div sd-user-permissions data-permission="users-manage" data-user="user" data-model="model" ng-show="model"></div>
         * 
         * Checking for a role:
         * <div sd-user-permissions data-permission="users-manage" data-role="role" data-model="model" ng-show="model"></div>
         * 
         * Checking for current user:
         * <div sd-user-permissions data-permission="users-manage" data-model="model" ng-show="model"></div>
         * 
         * Params:
         * @param {String} dataPermission - id of required permission.
         * @param {Object} dataUser
         * @param {String} dataRole
         * @param {Object} dataModel - model to assign permission to
         */
        .directive('sdUserPermissions', ['permissions', 'userPermissions', function(permissions, userPermissions) {
            return {
                scope: {
                    permission: '@',
                    user: '=',
                    role: '@',
                    model: '='
                },
                link: function(scope, element, attrs) {
                    scope.model = false;
                    if (permissions[scope.permission]) {
                        var requiredPermissions = permissions[scope.permission].permissions;
                        if (scope.role) {
                            scope.model = userPermissions.isRoleAllowed(requiredPermissions, scope.role);
                        } else {
                            scope.model = userPermissions.isUserAllowed(requiredPermissions, scope.user);
                        }
                    }
                }
            };
        }]);
});
