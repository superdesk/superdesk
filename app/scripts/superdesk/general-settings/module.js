define([
    'angular',
    'bootstrap_ui',
    './controllers/main',
    './controllers/addSource',
    './directives',
    './resources'
], function(angular) {
    'use strict';

    angular.module('superdesk.generalSettings', [
        'superdesk.generalSettings.directives',
        'superdesk.settings.entity',
        'superdesk.directives',
        'ui.bootstrap'
    ])
        .controller('AddSourceModalCtrl', require('superdesk/general-settings/controllers/addSource'))
        .config(function($routeProvider) {
            $routeProvider
                .when('/settings/', {
                    controller: require('superdesk/general-settings/controllers/main'),
                    templateUrl: 'scripts/superdesk/general-settings/views/main.html',
                    menu: {
                        label: gettext('Settings'),
                        priority: 0
                    }
                });
        });
});
