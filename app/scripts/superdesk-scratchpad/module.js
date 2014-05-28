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
                icon: 'plus',
                controller: ['scratchpad', 'data', function(scratchpad, data) {
                    scratchpad.addItem(data.item);
                }],
                filters: [
                    {action: 'addToScratchpad', type: 'archive'}
                ]
            });
    }]);

    return app;
});
