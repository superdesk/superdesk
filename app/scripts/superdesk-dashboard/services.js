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