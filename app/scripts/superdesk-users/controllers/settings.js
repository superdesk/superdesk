define(['angular', 'lodash'], function(angular, _) {
    'use strict';

    return ['$q', '$scope', 'em', 'superdesk', 'permissionsService', function ($q, $scope, em, superdesk, permissionsService) {
        $scope.permissions = superdesk.permissions;
        $scope.selectedRole = null;
        $scope.selectedRoleParent = null;
        $scope.editRole = null;
        $scope.editRoleParent = null;

        function loadRoles() {
            var delay = $q.defer();

            em.repository('user_roles').matching().then(function(roles) {
                $scope.roles = roles;
                $scope.rolePermissions = {};
                _.forEach($scope.roles._items, function(role) {
                    $scope.rolePermissions[role._id] = {};
                    _.forEach(superdesk.permissions, function(permission, id) {
                        permissionsService.isRoleAllowed(permission.permissions, role).then(function(isAllowed) {
                            $scope.rolePermissions[role._id][id] = isAllowed;
                            delay.resolve($scope.roles);
                        });
                    });
                });
            });

            return delay.promise;
        }

        loadRoles();

        $scope.selectRole = function(role) {
            $scope.selectedRole = role;
            $scope.selectedRoleParent = null;
            if (role['extends']) {
                _.forEach($scope.roles._items, function(item) {
                    if (item._id === role['extends']) {
                        $scope.selectedRoleParent = item;
                    }
                });
            }
        };

        $scope.$watch('editRole', function(editRole) {
            $scope.selectedRole = null;
            $scope.editRoleParent = null;
            if (editRole) {
                if (editRole['extends']) {
                    $scope.editRoleParent = _.find($scope.roles._items, {_id: editRole['extends']});
                }

                $scope.editPermissions = _.extend({}, superdesk.permissions);
                _.each($scope.editPermissions, function(p, k) {
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
