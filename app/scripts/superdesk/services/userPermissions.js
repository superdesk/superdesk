define(['angular'], function(angular) {
    'use strict';

    angular.module('superdesk.services.userPermissions', [])
        .service('userPermissions', ['storage', function(storage) {

            this.check = function(permissions, user) {
                if (!user) {
                    user = storage.getItem('auth').user;
                }
                // TODO: actual permissions checking from server
                return false;
            };

        }]);
});
