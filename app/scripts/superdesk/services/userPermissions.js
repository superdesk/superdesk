define(['angular'], function(angular) {
    'use strict';

    angular.module('superdesk.services.userPermissions', [])
        .service('userPermissions', ['$rootScope', 'em', function($rootScope, em) {

            this.isRoleAllowed = function(permissions, role) {
                if (!role) {
                    // TODO: should use current user's role
                    return false;
                }

                var allowed = true;
                _.forEach(permissions, function(methods, resource) {
                    _.forEach(methods, function(status, method) {
                        allowed = allowed && role.permissions && role.permissions[resource] && role.permissions[resource][method] && role.permissions[resource][method] === true;
                    });
                });

                return allowed;
            };

        }]);
});
