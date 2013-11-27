define([
    'angular',
    'angular-route'
], function(angular) {
    'use strict';

    angular.module('superdesk.services.permissions', [])
        .provider('permissions', [function() {
            var permissions = {};

            return {
                $get: function() {
                    return permissions;
                },
                permission: function(id, permission) {
                    permissions[id] = permission;
                }
            };

        }]);

});