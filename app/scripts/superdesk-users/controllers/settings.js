define(['angular', 'lodash'], function(angular, _) {
    'use strict';

    return ['$scope', 'em', 'permissions', function ($scope, em, permissions) {

        $scope.permissions = permissions;

        em.repository('user_roles').matching().then(function(roles) {
            $scope.roles = roles;
        });

        $scope.edit = function (role) {
            $scope.selectedRole = role;
        };

        $scope.addRole = function() {
            var newRole = {'name' : 'sample name', 'permissions' : permissions};
            $scope.userRoles.unshift(newRole);
            $scope.selectedRole = newRole;
        };

        $scope.cancelAddModal = function() {
            $scope.editRole = null;
        };

        $scope.openAddModal = function() {
            $scope.addModal = true;
            $scope.editRole = {};
            $scope.editPermissions = permissions;
        };

        $scope.save = function() {
            $scope.editRole.permissions = {};

            var selectedPermissions = _.where($scope.editPermissions, 'selected');
            _.each(selectedPermissions, function(permission) {
                _.merge($scope.editRole.permissions, permission.requires);
            });

            em.create('user_roles', $scope.editRole).then(function(role) {
                _.extend(role, $scope.editRole);
                $scope.roles._items.unshift(role);
                $scope.selectedRole = role;
                $scope.editRole = null;
            });
        };

        $scope.isAllowed = function (role, permission) {
            if (!role) {
                return false;
            }

            var allowed = true;
            _.each(permission.requires, function(methods, resource) {
                _.each(methods, function(val, method) {
                    allowed = allowed && role.permissions[resource][method];
                });
            });

            return allowed;
        };
    }];
});