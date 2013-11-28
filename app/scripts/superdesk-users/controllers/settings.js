define(['angular', 'lodash'], function(angular, _) {
    'use strict';

    return ['$scope', 'permissions',
        function($scope,permissions) {

            $scope.userRoles = [
                {
                    'name' : 'administrator',
                    'permissions' : permissions,
                    'items' : [
                        {
                            'name' : 'editor',
                            'permissions' : permissions
                        },
                        {
                            'name' : 'journalist',
                            'permissions' : permissions
                        },
                        {
                            'name' : 'desk manager',
                            'permissions' : permissions
                        }
                    ]
                },
                {
                    'name' : 'superadmin',
                    'permissions' : permissions
                },
                {
                    'name' : 'editor',
                    'permissions' : permissions,
                    'items' : [
                        {
                            'name' : 'journalist',
                            'permissions' : permissions,
                            'items' : [
                                {
                                    'name' : 'writer',
                                    'permissions' : permissions
                                },
                                {
                                    'name' : 'staff guy',
                                    'permissions' : permissions
                                }
                            ]
                        
                        },
                        {
                            'name' : 'desk manager',
                            'permissions' : permissions
                        }
                    ]
                },
                {
                    'name' : 'journalist',
                    'permissions' : permissions
                },
                {
                    'name' : 'data analyst',
                    'permissions' : permissions
                },
                {
                    'name' : 'seo expert',
                    'permissions' : permissions
                },
                {
                    'name' : 'chief editor',
                    'permissions' : permissions
                },
                {
                    'name' : 'desk manager',
                    'permissions' : permissions
                }
            ];

            $scope.selectedRole = null;

            $scope.editRole = function(role) {
                $scope.selectedRole = role;
            };

            $scope.closeEdit = function() {
                $scope.selectedRole = null;
            };

            $scope.addRole = function() {
                var newRole = {'name' : 'sample name', 'permissions' : permissions};
                $scope.userRoles.unshift(newRole);
                $scope.selectedRole = newRole;
            };

            $scope.save = function() {
                //do save
            };

        }];
});