define(['angular'], function(angular) {
    'use strict';

    angular.module('superdesk.services.userPermissions', [])
        .service('userPermissions', ['$rootScope', 'em', function($rootScope, em) {

            this.isUserAllowed = function(permissions, user) {
                var self = this;

                if (!user) {
                    user = $rootScope.currentUser;
                }
                if (user.role) {
                    if (typeof user.role === 'string') {
                        return em.repository('user_roles').find(user.role).then(function(role) {
                            return self.isRoleAllowed(permissions, role);
                        });
                    } else {
                        return this.isRoleAllowed(permissions, user.role);
                    }
                } else {
                    return false;
                }
            };

            this.isRoleAllowed = function(permissions, role) {
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
