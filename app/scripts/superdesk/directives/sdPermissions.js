define(['angular'], function(angular) {
    'use strict';

    return angular.module('superdesk.permissions.directives', [])
        /**
         * sdPermissions checks if user has specified permissions and assigns
         * to specified model to use in displaying/hiding/disabling elements.
         *
         * Usage:
         * Checking for a user:
         * <div sd-permissions data-permission="users-manage" data-user="user" data-model="model" ng-show="model"></div>
         *
         * Checking for a role:
         * <div sd-permissions data-permission="users-manage" data-role="role" data-model="model" ng-show="model"></div>
         *
         * Checking for current user (default if no user/role specified):
         * <div sd-permissions data-permission="users-manage" data-model="model" ng-show="model"></div>
         *
         * Params:
         * @scope {Object} dataModel - model to assign permission to
         * @scope {String} dataPermission - id of required permission.
         * @scope {Object} dataRole - role to check
         * @scope {Object} dataUser - user to check
         */
        .directive('sdPermissions', ['permissions', 'permissionsService', function(permissions, permissionsService) {
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
                            scope.model = permissionsService.isRoleAllowed(requiredPermissions, scope.role);
                        } else if (scope.user) {
                            permissionsService.isUserAllowed(requiredPermissions, scope.user).then(function(result) {
                                scope.model = result;
                            });
                        } else {
                            permissionsService.isUserAllowed(requiredPermissions).then(function(result) {
                                scope.model = result;
                            });
                        }

                    }
                }
            };
        }]);
});
