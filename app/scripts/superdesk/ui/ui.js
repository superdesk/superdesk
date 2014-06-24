define([
    'angular',
    'require',
    './shadow-directive',
    './autoheight-directive'
], function(angular, require) {
    'use strict';

    return angular.module('superdesk.ui', [])

        .directive('sdShadow', require('./shadow-directive'))
        .directive('sdAutoHeight', require('./autoheight-directive'));
});
