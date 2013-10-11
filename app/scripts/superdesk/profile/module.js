define([
    'angular',
    'angular-route',
    'uploader-angular',
    './controllers/main',
    './controllers/upload-avatar',
    './directives',
    './resources',
], function(angular) {
    'use strict';

    angular.module('superdesk.profile', ['ngRoute', 'blueimp.fileupload', 'superdesk.profile.directives', 'superdesk.profile.resources', 'superdesk.profile.directives.uploadavatar']).
        config(function($routeProvider) {
            $routeProvider.
                when('/my-profile', {
                    controller: require('superdesk/profile/controllers/main'),
                    templateUrl: 'scripts/superdesk/profile/views/main.html',
                });
        });
});
