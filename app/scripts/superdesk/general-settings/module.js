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
        'superdesk.generalSettings.controllers',
        'superdesk.generalSettings.resources',
        'superdesk.directives',
        'ui.bootstrap'
    ])
        .config(function($routeProvider) {
            $routeProvider.
                when('/settings/', {
                    controller: require('superdesk/general-settings/controllers/main'),
                    templateUrl: 'scripts/superdesk/general-settings/views/main.html',
                    menu: {
                        label: gettext('Settings'),
                        priority: 0
                    }
                });
        });

});
