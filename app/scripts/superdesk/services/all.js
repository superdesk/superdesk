define([
    'angular',
    './translate',
    './upload',
    './notify',
    './settings',
    '../userSettings',
    '../entity',
    '../server'
], function() {
    'use strict';

    angular.module('superdesk.services', [
        'superdesk.services.translate',
        'superdesk.services.upload',
        'superdesk.services.notify',
        'superdesk.services.settings',
        'superdesk.userSettings',
        'superdesk.entity',
        'superdesk.server'
    ]);
});