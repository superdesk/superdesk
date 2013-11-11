define(['angular', 'lodash'], function(angular, lodash) {
    'use strict';

    angular.module('superdesk.dashboard.services', ['superdesk.dashboard.providers'])
        .service('widgetService', ['$q', 'storage', 'widgets', function($q, storage, widgets) {
            var widgetKey = 'dashboard:widgets';
            var configurationKey = 'dashboard:widgets:configuration';

            this.load = function() {
                var userWidgets = storage.getItem(widgetKey) || {};
                angular.forEach(userWidgets, function(userWidget, wcode) {
                    userWidgets[wcode] = angular.extend(widgets[wcode], userWidget);
                });

                return userWidgets;
            };

            this.save = function(userWidgets) {
                var config = {};
                angular.forEach(userWidgets, function(widget, wcode) {
                    config[wcode] = _.pick(widget, ['col', 'row', 'sizex', 'sizey', 'wcode']);
                });
                storage.setItem(widgetKey, config, true);
            };

            this.loadConfiguration = function(wcode) {
                var configuration = storage.getItem(configurationKey);
                if (configuration && configuration[wcode]) {
                    return configuration[wcode];
                } else {
                    return null;
                }
            };

            this.saveConfiguration = function(wcode, configuration) {
                var config = storage.getItem(configurationKey) || {};
                config[wcode] = configuration;
                storage.setItem(configurationKey, config, true);
            };

        }]);
});