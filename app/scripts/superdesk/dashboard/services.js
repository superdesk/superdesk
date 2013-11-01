define(['angular'], function(angular) {
    'use strict';

    angular.module('superdesk.dashboard.services', ['superdesk.dashboard.providers'])
        .service('widgetService', ['$q', 'storage', function($q, storage) {
            var storageKey = 'dashboard:widgets';

            var widgetService = {
                load: function() {
                    var widgets = storage.getItem(storageKey);
                    if (widgets === null) {
                        widgets = {};
                        this.save(widgets);
                    }
                    return widgets;
                },
                save: function(widgets) {
                    storage.setItem(storageKey, widgets, true);
                }
            };

            return widgetService;
        }]);
});