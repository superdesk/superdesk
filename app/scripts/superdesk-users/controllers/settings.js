define(['angular', 'lodash'], function(angular, _) {
    'use strict';

    return ['$scope', 'em', 'permissions', 'userPermissions', function ($scope, em, permissions, userPermissions) {

        $scope.permissions = permissions;

        em.repository('user_roles').matching().then(function(roles) {
            /*
            _.forEach(roles._items, function(item) {
                em.remove(item);
            });
            //*/
            $scope.roles = roles;
        });

        $scope.preview = function (role) {
            $scope.selectedRole = role;
        };

        var newRole = false;

        $scope.edit = function (role) {
            $scope.editRole = role;
            $scope.newRole = false;
            $scope.editPermissions = permissions;
            _.each($scope.editPermissions,function(p,key){
                if ($scope.isAllowed($scope.editRole, p)) {
                    p.selected = true;
                }
            });
        };

        $scope.cancelAddModal = function() {
            $scope.editRole = null;
            $scope.editPermissions = null;
        };

        $scope.openAddModal = function() {
            $scope.editRole = {};
            newRole = true;
            $scope.editPermissions = permissions;
        };

        $scope.save = function() {
            $scope.editRole.permissions = {};

            var selectedPermissions = _.where($scope.editPermissions, 'selected');
            _.each(selectedPermissions, function(permission) {
                _.merge($scope.editRole.permissions, permission.permissions);
            });


            if (newRole) {
                em.create('user_roles', $scope.editRole).then(function(role) {
                    _.extend(role, $scope.editRole);
                    $scope.roles._items.unshift(role);
                    $scope.selectedRole = role;
                    $scope.editRole = null;
                    $scope.editPermissions = null;
                });
            }
            else {
                em.update($scope.editRole, $scope.editRole).then(function(role) {
                    $scope.selectedRole = role;
                    $scope.editRole = null;
                    $scope.editPermissions = null;
                });
            }

        };

        $scope.isAllowed = function (role, permission) {
            return userPermissions.isRoleAllowed(permission.permissions, role);
        };
    }];
});