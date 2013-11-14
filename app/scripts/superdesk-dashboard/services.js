define(['lodash', 'angular'], function(_, angular) {
    'use strict';

    angular.module('superdesk.dashboard.services', [])
        /**
         * Widgets registry
         */
        .provider('widgets', [function() {
            var widgets = {};

            return {
                $get: function() {
                    return widgets;
                },

                /**
                 * Register a widget with given id
                 *
                 * @param {string} id
                 * @param {Object} widget
                 */
                widget: function(id, widget) {
                    angular.extend(widget, {wcode: id});
                    widgets[id] = widget;
                    return this;
                }
            };
        }])
        .service('widgetService', ['storage', 'widgets', function(storage, widgets) {
            var widgetKey = 'dashboard:widgets';
            var configurationKey = 'dashboard:widgets:configuration';

            this.load = function() {
                var userWidgets = storage.getItem(widgetKey) || {};
                var configuration = storage.getItem(configurationKey) || {};
                angular.forEach(userWidgets, function(userWidget, wcode) {
                    userWidgets[wcode] = angular.extend(widgets[wcode], userWidget);
                    userWidgets[wcode].configuration = angular.extend(userWidgets[wcode].configuration, configuration[wcode]);
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

            this.saveConfiguration = function(wcode, configuration) {
                var config = storage.getItem(configurationKey) || {};
                config[wcode] = configuration;
                storage.setItem(configurationKey, config, true);
            };

        }]);
});