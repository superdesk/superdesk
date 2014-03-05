define([
    'angular',
    'require',
    './resource-provider'
], function(angular, require) {
    'use strict';

    return angular.module('superdesk.data', ['superdesk'])
        .provider('resource', require('./resource-provider'));
});
