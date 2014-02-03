define([
    'angular',
    'lodash',
    './services',
    './directives'
], function(angular, _) {
    'use strict';

    var app = angular.module('superdesk.scratchpad', [
        'superdesk.scratchpad.services',
        'superdesk.scratchpad.directives'
    ]);
});
