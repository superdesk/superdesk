define(['angular'], function(angular) {
    'use strict';

    angular.module('superdesk.services.permissionsService', [])
        .service('permissionsService', ['$q', '$rootScope', 'em', function($q, $rootScope, em) {

            this.isUserAllowed = function(permissions, user) {
                var self = this;

                var delay = $q.defer();

                if (!user) {
                    user = $rootScope.currentUser;
                }
                if (user.role) {
                    if (typeof user.role === 'string') {
                        em.repository('user_roles').find(user.role).then(function(role) {
                            delay.resolve(self.isRoleAllowed(permissions, role));
                        });
                    } else {
                        delay.resolve(this.isRoleAllowed(permissions, user.role));
                    }
                } else {
                    delay.resolve(false);
                }

                return delay.promise;
            };

            this.isRoleAllowed = function(permissions, role) {
                var self = this;

                var delay = $q.defer();

                var allowed = true;

                _.forEach(permissions, function(methods, resource) {
                    _.forEach(methods, function(status, method) {
                        allowed = allowed && role.permissions && role.permissions[resource] && role.permissions[resource][method] && role.permissions[resource][method] === true;
                    });
                });

                allowed = allowed || false;

                if (!allowed && role.extends) {
                    em.repository('user_roles').find(role.extends).then(function(extendedFrom) {
                        delay.resolve(self.isRoleAllowed(permissions, extendedFrom));
                    });
                } else {
                    delay.resolve(allowed);
                }

                return delay.promise;
            };

        }]);
});
