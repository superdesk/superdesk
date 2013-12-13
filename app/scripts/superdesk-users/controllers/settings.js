define(['angular', 'lodash'], function(angular, _) {
    'use strict';

    return ['$q', '$scope', 'em', 'permissions', 'permissionsService', function ($q, $scope, em, permissions, permissionsService) {

        $scope.permissions = permissions;
        $scope.selectedRole = null;
        $scope.selectedRoleParent = null;
        $scope.editRole = null;
        $scope.editRoleParent = null;

        var loadRoles = function() {
            var delay = $q.defer();

            em.repository('user_roles').matching().then(function(roles) {
                $scope.roles = roles;
                $scope.rolePermissions = {};
                _.forEach($scope.roles._items, function(role) {
                    $scope.rolePermissions[role._id] = {};
                    _.forEach(permissions, function(permission, id) {
                        permissionsService.isRoleAllowed(permission.permissions, role).then(function(isAllowed) {
                            $scope.rolePermissions[role._id][id] = isAllowed;
                            delay.resolve($scope.roles);
                        });
                    });
                });
            });

            return delay.promise;
        };

        loadRoles();

        $scope.$watch('selectedRole', function(selectedRole) {
            $scope.selectedRoleParent = null;
            if (selectedRole) {
                if (selectedRole.extends) {
                    _.forEach($scope.roles._items, function(role) {
                        if (role._id === selectedRole.extends) {
                            $scope.selectedRoleParent = role;
                        }
                    });
                }
            }
        }, true);

        $scope.$watch('editRole', function(editRole) {
            $scope.selectedRole = null;
            $scope.editRoleParent = null;
            if (editRole) {
                if (editRole.extends) {
                    _.forEach($scope.roles._items, function(role) {
                        if (role._id === editRole.extends) {
                            $scope.editRoleParent = role;
                        }
                    });
                }
                $scope.editPermissions = _.extend({}, permissions);
                _.each($scope.editPermissions, function(p, k){
                    if (editRole._id) {
                        p.selected  = $scope.rolePermissions[editRole._id][k];
                    } else {
                        p.selected = false;
                    }
                    if ($scope.editRoleParent) {
                        p.inherited = $scope.rolePermissions[$scope.editRoleParent._id][k];
                    } else {
                        p.inherited = false;
                    }
                });
            }
        }, true);

        $scope.cancel = function() {
            $scope.editRole = null;
            $scope.editPermissions = null;
        };

        $scope.save = function() {
            var selectedPermissions = _.where($scope.editPermissions, 'selected');
            if (!$scope.editRole.permissions) {
                $scope.editRole.permissions = {};
            }
            $scope.editRole.permissions = {};
            _.each(selectedPermissions, function(permission) {
                _.merge($scope.editRole.permissions, permission.permissions);
            });
            if ($scope.editRole._id) {
                em.update($scope.editRole).then(function(role) {
                    loadRoles().then(function(roles) {
                        $scope.cancel();
                    });
                });
            } else {
                em.create('user_roles', $scope.editRole).then(function(role) {
                    loadRoles().then(function(roles) {
                        $scope.cancel();
                    });
                });
            }
        };
        
    }];
});