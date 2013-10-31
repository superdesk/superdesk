define([
    'angular',
    './translate',
    './upload',
    './notify',
    './general-settings',
    '../settings',
    '../entity',
    '../server'
], function() {
    'use strict';

    angular.module('superdesk.services', [
        'superdesk.services.translate',
        'superdesk.services.upload',
        'superdesk.services.notify',
        'superdesk.services.generalSettings',
        'superdesk.settings',
        'superdesk.entity',
        'superdesk.server'
    ]);
});