define([
    'angular',
    'require',
    './shadow-directive'
], function(angular, require) {
    'use strict';

    return angular.module('superdesk.ui', [])

        .directive('sdShadow', require('./shadow-directive'));
});
