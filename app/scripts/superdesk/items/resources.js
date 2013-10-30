define(['angular'], function(angular) {
    'use strict';

    angular.module('superdesk.items.resources', ['superdesk.server'])
        .service('ItemService', function(server) {
            return {
                update: function(item) {
                    server.update(item);
                }
            };
        })
        .factory('feedSources', function($resource) {
            return $resource('scripts/superdesk/items/static-resources/sources.json');
        });
});
