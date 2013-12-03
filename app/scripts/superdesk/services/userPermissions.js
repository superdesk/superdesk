define(['angular'], function(angular) {
    'use strict';

    angular.module('superdesk.services.userPermissions', [])
        .service('userPermissions', ['storage', function(storage) {

            this.isUserAllowed = function(permissions, user) {
                if (!user) {
                    user = storage.getItem('auth').user;
                }
                // TODO: actual permissions checking from server
                return false;
            };

            this.isRoleAllowed = function(permissions, role) {
                if (!role) {
                    // TODO: should use current user's role
                    return false;
                }

                var allowed = true;
                _.forEach(permissions, function(methods, resource) {
                    _.forEach(methods, function(method) {
                        allowed = allowed && role.permissions && role.permissions[resource] && role.permissions[resource].indexOf(method) !== -1;
                    });
                });

                return allowed;
            };

        }]);
});
