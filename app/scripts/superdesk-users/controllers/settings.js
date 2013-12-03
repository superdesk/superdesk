define(['angular', 'lodash'], function(angular, _) {
    'use strict';

    return ['$scope', 'em', 'permissions', function ($scope, em, permissions) {

        $scope.permissions = permissions;

        em.repository('user_roles').matching().then(function(roles) {
            $scope.roles = roles;
        });

        $scope.preview = function (role) {
            $scope.selectedRole = role;
            $scope.selectedRoleParent = null;
            if (role.child_of) {
                $scope.selectedRoleParent = $scope.roles._items[_.findKey($scope.roles._items, {_id:role.child_of})];
            }
        };

        //flag for add/editng
        var newRole = false;

        $scope.edit = function (role) {
            
            $scope.editRole =  role;
            $scope.newRole = false;
            
            //reset editPermission object
            $scope.editPermissions = _.extend({},permissions);

            //set checked elements
            _.each($scope.editPermissions,function(p,key){
                if ($scope.isAllowed($scope.editRole, p)) {
                    p.selected = true;
                }
            });
        };

        $scope.cancel = function() {
            $scope.editRole = null;
            $scope.editPermissions = null;
        };

        $scope.add = function() {
            $scope.editRole = {};
            newRole = true;
            $scope.editPermissions = _.extend({},permissions);
        };

        $scope.save = function() {

            $scope.editRole.permissions = {};

            var selectedPermissions = _.where($scope.editPermissions, 'selected');
            _.each(selectedPermissions, function(permission) {
                _.merge($scope.editRole.permissions, permission.requires);
            });


            if (newRole) {
                em.create('user_roles', $scope.editRole).then(function(role) {
                    _.extend(role, $scope.editRole);
                    $scope.roles._items.unshift(role);
                    
                    $scope.preview(role);
                    $scope.cancel();
                });
            }
            else {
                em.update($scope.editRole, $scope.editRole).then(function(role) {//?

                    $scope.preview(role);
                    $scope.cancel();
                });
            }

        };


        $scope.isAllowed = function (role, permission) {
            if (!role) {
                return false;
            }

            var allowed = true;

            _.each(permission.requires, function(methods, resource) {
                _.each(methods, function(val,method) {
                    if (role.permissions[resource] !== undefined) {
                        allowed = allowed && role.permissions[resource][method];
                    }
                    else {
                        allowed = false;
                    }
                });
            });

            return allowed;
        };
    }];
});