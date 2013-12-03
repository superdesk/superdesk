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
            if (role && role.child_of) {
                $scope.selectedRoleParent = $scope.roles._items[_.findKey($scope.roles._items, {_id:role.child_of})];
            }
        };

        var newRole = false;

        var getPermissions = function() {

            $scope.editPermissions = _.extend({},permissions);

            var isRole = $scope.editRole !== null && $scope.editRole!==undefined && !_.isEmpty($scope.editRole);

            if (isRole && $scope.editRole.child_of) {
                //if we have parent, check what fields are set (and unchangeable)
                var parent = $scope.roles._items[_.findKey($scope.roles._items, {_id:$scope.editRole.child_of})];
                _.each($scope.editPermissions,function(p,key){
                    if ($scope.isAllowed(parent, p)) {
                        p.disable = true;
                    }
                    else {
                        p.disable = false;
                    }
                });
            } else {
                _.each($scope.editPermissions,function(p,key){
                    p.disable = false;
                });
            }

            //check what fields we have checked (set by role itself)
            if (isRole && $scope.editRole.permissions) {
                _.each($scope.editPermissions,function(p,key){
                    if ($scope.isAllowed($scope.editRole, p)) {
                        p.selected = true;
                    }
                    else {
                        p.selected = false;
                    }
                });
            }
        };

        $scope.$watch('editRole.child_of',function(oldVal,newVal){
            getPermissions();
        });

        $scope.edit = function(role) {

            if (role === undefined && role === null) { //new one
                $scope.editRole = {};
                newRole = true;
            }
            else { //editing
                $scope.editRole = role;
                $scope.newRole = false;
            }

        };

        $scope.cancel = function() {
            $scope.editRole = null;
            $scope.editPermissions = null;
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
                em.update($scope.editRole, $scope.editRole).then(function(role) {
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
            if (permission) {
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
            }
            else {
                return false;
            }
            
            
        };
    }];
});