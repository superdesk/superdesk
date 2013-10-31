define([
    'angular',
    './translate',
    './upload',
    './notify',
    './general-settings',
    '../userSettings',
    '../entity',
    '../server'
], function() {
    'use strict';

    angular.module('superdesk.services', [
        'superdesk.services.translate',
        'superdesk.services.upload',
        'superdesk.services.notify',
        'superdesk.services.generalSettings',
        'superdesk.userSettings',
        'superdesk.entity',
        'superdesk.server'
    ]);
});