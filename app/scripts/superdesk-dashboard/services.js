define(['angular', 'lodash'], function(angular, lodash) {
    'use strict';

    angular.module('superdesk.dashboard.services', ['superdesk.dashboard.providers'])
        .service('widgetService', ['$q', 'storage', 'widgets', function($q, storage, widgets) {
            var storageKey = 'dashboard:widgets';

            this.load = function() {
                var userWidgets = storage.getItem(storageKey) || {};
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
                storage.setItem(storageKey, config, true);
            };
        }]);
});