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
                    widgetList[id] = data;
                    return this;
                }
            };

        }]);

});