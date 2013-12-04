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
         * Checking for a user by username:
         * <div sd-user-permissions data-permission="users-manage" data-user-name="username" data-model="model" ng-show="model"></div>
         * 
         * Checking for a role by name:
         * <div sd-user-permissions data-permission="users-manage" data-role-name="rolename" data-model="model" ng-show="model"></div>
         * 
         * Checking for current user (default if no user/role/userName/roleName specified):
         * <div sd-user-permissions data-permission="users-manage" data-model="model" ng-show="model"></div>
         * 
         * Params:
         * @param {Object} dataModel - model to assign permission to
         * @param {String} dataPermission - id of required permission.
         * @param {String} dataRoleName - name of role to check
         * @param {String} dataUserName - username of user to check
         * @param {Object} dataRole - role to check
         * @param {Object} dataUser - user to check
         */
        .directive('sdUserPermissions', ['em', 'permissions', 'userPermissions', function(em, permissions, userPermissions) {
            return {
                scope: {
                    model: '=',
                    permission: '@',
                    roleName: '@',
                    userName: '@',
                    role: '=',
                    user: '='
                },
                link: function(scope, element, attrs) {
                    scope.model = false;
                    if (permissions[scope.permission]) {
                        var requiredPermissions = permissions[scope.permission].permissions;
                        if (scope.roleName) {
                            em.repository('user_roles').matching({name: scope.roleName}).then(function(roles) {
                                // TODO: matching doesn't work
                                _.forEach(roles._items, function(role) {
                                    if (role.name === scope.roleName) {
                                        scope.model = userPermissions.isRoleAllowed(requiredPermissions, role);
                                    }
                                });
                            });
                        } else if (scope.userName) {
                            em.repository('users').matching({username: scope.userName}).then(function(users) {
                                // TODO: matching doesn't work
                                _.forEach(users._items, function(user) {
                                    if (user.username === scope.userName) {
                                        userPermissions.isUserAllowed(requiredPermissions, user).then(function(result) {
                                            scope.model = result;
                                        });
                                    }
                                });
                            });
                        } else if (scope.role) {
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
