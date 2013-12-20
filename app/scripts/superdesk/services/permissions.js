define(['angular'], function(angular) {
    'use strict';

    angular.module('superdesk.services')
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
