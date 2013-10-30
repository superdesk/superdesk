define([
    'angular',
    './translate',
    './upload',
    './notify',
    '../settings',
    '../entity',
    '../server'
], function() {
    'use strict';

    angular.module('superdesk.services', [
        'superdesk.services.translate',
        'superdesk.services.upload',
        'superdesk.services.notify',
        'superdesk.settings',
        'superdesk.entity',
        'superdesk.server'
    ]);
});