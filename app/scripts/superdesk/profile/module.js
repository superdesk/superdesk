define([
    'angular',
    'file-upload/jquery.fileupload-angular',
    './controllers/main',
    './controllers/upload-avatar',
    './directives',
    './resources',
], function(angular) {
    'use strict';

    angular.module('superdesk.profile', ['blueimp.fileupload', 'superdesk.profile.directives', 'superdesk.profile.resources', 'superdesk.profile.directives.uploadavatar']).
        config(function($routeProvider) {
            $routeProvider.
                when('/my-profile', {
                    controller: require('superdesk/profile/controllers/main'),
                    templateUrl: 'scripts/superdesk/profile/views/main.html',
                    resolve: {
                        user: function($rootScope, server) {
                            return server.readItem('users', $rootScope.currentUser.username);
                        }
                    }
                });
        });
});
