define([
    'angular',
    'require',
    './directives'
], function(angular, require) {
    'use strict';

    return angular.module('superdesk.items-common', ['superdesk.items-common.directives']);
});
