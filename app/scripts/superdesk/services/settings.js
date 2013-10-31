define(['angular'], function(angular) {
    'use strict';

    angular.module('superdesk.services.settings', [])
        .provider('settings', [function() {
            var settings = {};
            
            return {
                $get: function() {
                    return settings;
                },
                register: function(id, options) {
                    settings[id] = options;
                }
            };

        }]);

});