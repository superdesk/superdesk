define(['angular'], function(angular) {
    'use strict';

    angular.module('superdesk.dashboard.providers', [])
        .provider('widgets', [function() {
            var widgetList = {};

            return {
                $get: function() {
                    return widgetList;
                },
                widget: function(id, data) {
                    angular.extend(data, {wcode: id});
                    widgetList[id] = data;
                    return this;
                }
            };
        }]);
});