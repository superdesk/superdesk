define(['angular', 'angular-resource'], function(angular) {
    'use strict';

    angular.module('superdesk.dashboard.services', ['superdesk.dashboard.providers'])
        .service('widgetService', ['storage', 'widgets', function(storage, widgets) {
            var widgetKey = 'dashboard:widgets';
            var configurationKey = 'dashboard:widgets:configuration';

            this.load = function() {
                var userWidgets = storage.getItem(widgetKey) || {};
                var configuration = storage.getItem(configurationKey) || {};
                
                angular.forEach(userWidgets, function(userWidget, id) {
                    userWidgets[id] = angular.extend({}, widgets[userWidget.wcode], userWidget);
                    userWidgets[id].configuration = angular.extend({}, userWidgets[id].configuration, configuration[id]);
                });

                /*
                angular.forEach(userWidgets, function(userWidget, wcode) {
                    userWidgets[wcode] = angular.extend(widgets[wcode], userWidget);
                    userWidgets[wcode].configuration = angular.extend(userWidgets[wcode].configuration, configuration[wcode]);
                });
                */

                return userWidgets;
            };

            this.save = function(userWidgets) {
                var config = {};
                angular.forEach(userWidgets, function(widget, wcode) {
                    config[wcode] = _.pick(widget, ['col', 'row', 'sizex', 'sizey', 'wcode']);
                });
                storage.setItem(widgetKey, config, true);
            };

            this.saveConfiguration = function(id, configuration) {
                var config = storage.getItem(configurationKey) || {};
                config[id] = configuration;
                storage.setItem(configurationKey, config, true);
            };

        }]);
});