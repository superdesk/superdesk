define([
    'angular',
    'require',
    './directives',
    './directives/sidebar-layout'
], function(angular, require) {
    'use strict';

    return angular.module('superdesk.items-common', ['superdesk.items-common.directives']);
});
