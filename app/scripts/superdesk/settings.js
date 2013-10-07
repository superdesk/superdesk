define(['angular'], function(angular) {
    'use strict';

    angular.module('superdesk.settings', []).
        service('settings', ['storage', function(storage) {
            return new function() {
                this.initialize = function(pluginName, defaultSettings) {
                    var self = this;
                    var instance = angular.extend({}, defaultSettings);
                    instance.save = function() {
                        storage.setItem(pluginName + ':settings', self._clear(this), true);
                    };
                    instance.load = function() {
                        var settings = storage.getItem(pluginName + ':settings');
                        if (settings !== null) {
                            for (var i in settings) {
                                this[i] = settings[i];
                            }
                        } else {
                            this.save();
                        }
                    };
                    return instance;
                };
                this._clear = function(instance) {
                    var values = {};
                    for (var i in instance) {
                        if (i !== 'save' || i !== 'load') {
                            values[i] = instance[i];
                        }
                    }
                    return values;
                };
            };
        }]);
});