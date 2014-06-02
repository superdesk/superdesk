define(['lodash', 'angular'], function(_, angular) {
    'use strict';

    return ['storage', 'superdesk', function(storage, superdesk) {
        var widgetKey = 'dashboard:widgets';

        this.load = function() {
            var userWidgets = storage.getItem(widgetKey) || {};

            angular.forEach(userWidgets, function(userWidget, id) {
                userWidgets[id] = angular.extend({}, superdesk.widgets[userWidget.wcode], userWidget);
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
    }];
});
