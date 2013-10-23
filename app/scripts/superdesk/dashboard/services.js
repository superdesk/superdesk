define(['angular'], function(angular, widgetList) {
    'use strict';

    angular.module('superdesk.dashboard.services', []).
        service('widgetService', ['$q', 'storage', 'widgetResource', function($q, storage, widgetResource) {
            var storageKey = 'dashboard:widgets';
            
            var widgetService = {
                widgetList: [],
                fetchWidgetList: function() {
                    var self = this;
                    var delay = $q.defer();

                    widgetResource.get(function(data) {
                        self.widgetList = data;
                        delay.resolve(data);
                    });

                    return delay.promise;
                },
                getWidgetList: function() {
                    return this.widgetList;
                },
                loadWidgets: function() {
                    var widgets = storage.getItem(storageKey);
                    if (widgets === null) {
                        widgets = [];
                        this.saveWidgets(widgets);
                    }
                    return widgets;
                },
                saveWidgets: function(widgets) {
                    storage.setItem(storageKey, widgets, true);
                }
            };

            return widgetService;
        }]);
});