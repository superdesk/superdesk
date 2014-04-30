define([
    'angular',
    './scratchpad-directive',
    './scratchpad-service'
], function(angular, ScratchpadDirective, ScratchpadService) {
    'use strict';

    return angular.module('superdesk.scratchpad', [])
        .directive('sdScratchpad', ScratchpadDirective)
        .service('scratchpad', ScratchpadService);
});
