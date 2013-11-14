define(['angular'], function(angular) {
    'use strict';

    angular.module('superdesk.dashboard.providers', [])
        .provider('widgets', [function() {
            var widgetList = {};

            return {
                $get: function() {
                    return widgetList;
                },
                widget: function(wcode, data) {
                    angular.extend(data, {wcode: wcode});
                    widgetList[wcode] = data;
                    return this;
                }
            };
        }]);
});