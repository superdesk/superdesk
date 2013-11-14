define(['angular', 'angular-resource'], function(angular) {
    'use strict';

    angular.module('superdesk.dashboard.services', ['superdesk.dashboard.providers'])
        .service('widgetService', ['storage', 'widgets', function(storage, widgets) {
            var widgetKey = 'dashboard:widgets';

            this.load = function() {
                var userWidgets = storage.getItem(widgetKey) || {};
                
                angular.forEach(userWidgets, function(userWidget, id) {
                    userWidgets[id] = angular.extend({}, widgets[userWidget.wcode], userWidget);
                });

                return userWidgets;
            };

            this.save = function(userWidgets) {
                var config = {};
                angular.forEach(userWidgets, function(widget, id) {
                    config[id] = _.pick(widget, ['col', 'row', 'sizex', 'sizey', 'wcode', 'configuration']);
                });
                storage.setItem(widgetKey, config, true);
            };

            this.saveConfiguration = function(id, configuration) {
                var userWidgets = this.load();
                userWidgets[id].configuration = angular.extend(userWidgets[id].configuration, configuration);
                this.save(userWidgets);
            };

        }]);
});