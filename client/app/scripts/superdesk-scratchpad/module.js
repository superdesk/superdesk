define([
    'angular',
    './scratchpad-directive',
    './scratchpad-service'
], function(angular, ScratchpadDirective, ScratchpadService) {
    'use strict';

    var app = angular.module('superdesk.scratchpad', []);
    app.directive('sdScratchpad', ScratchpadDirective);
    app.service('scratchpad', ScratchpadService);

    app.config(['superdeskProvider', function(superdesk) {
        superdesk
            .activity('add.scratchpad', {
                label: gettext('Add to scratchpad'),
                icon: 'scratchpad-add',
                controller: ['scratchpad', 'data', function(scratchpad, data) {
                    scratchpad.addItem(data.item);
                }],
                filters: [
                    {action: 'list', type: 'archive'}
                ]
            })
            .activity('remove.scratchpad', {
                label: gettext('Remove from scratchpad'),
                icon: 'scratchpad-remove',
                controller: ['scratchpad', 'data', function(scratchpad, data) {
                    scratchpad.removeItem(data.item);
                }],
                filters: [
                    {action: 'removeScratchpad', type: 'scratchpad'}
                ]
            });
    }]);

    return app;
});
