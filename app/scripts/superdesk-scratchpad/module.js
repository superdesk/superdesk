define([
    'angular',
    'lodash',
    './services',
    './directives'
], function(angular, _) {
    'use strict';

    angular.module('superdesk.scratchpad', [
        'superdesk.scratchpad.services',
        'superdesk.scratchpad.directives'
    ]);
});
