define([
    'jquery',
    'angular'
], function($, angular) {
    'use strict';

    angular.module('superdesk.directives')
        /**
         * sdUserPermissions checks if user has specified permissions and assigns
         * to specified model to use in displaying/hiding/disabling elements.
         *
         * Usage:
         * Checking for a user:
         * <div sd-user-permissions data-permission="users-manage" data-user="user" data-model="model" ng-show="model"></div>
         * 
         * Checking for a role:
         * <div sd-user-permissions data-permission="users-manage" data-role="role" data-model="model" ng-show="model"></div>
         * 
         * Checking for current user (default if no user/role specified):
         * <div sd-user-permissions data-permission="users-manage" data-model="model" ng-show="model"></div>
         * 
         * Params:
         * @param {Object} dataModel - model to assign permission to
         * @param {String} dataPermission - id of required permission.
         * @param {Object} dataRole - role to check
         * @param {Object} dataUser - user to check
         */
        .directive('sdUserPermissions', ['permissions', 'userPermissions', function(permissions, userPermissions) {
            return {
                scope: {
                    model: '=',
                    permission: '@',
                    role: '=',
                    user: '='
                },
                link: function(scope, element, attrs) {
                    scope.model = false;
                    if (permissions[scope.permission]) {
                        var requiredPermissions = permissions[scope.permission].permissions;
                        if (scope.role) {
                            scope.model = userPermissions.isRoleAllowed(requiredPermissions, scope.role);
                        } else if (scope.user) {
                            userPermissions.isUserAllowed(requiredPermissions, scope.user).then(function(result) {
                                scope.model = result;
                            });
                        } else {
                            userPermissions.isUserAllowed(requiredPermissions).then(function(result) {
                                scope.model = result;
                            });
                        }

                    }
                }
            };
        }]);
});
