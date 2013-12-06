define(['angular'], function(angular) {
    'use strict';

    angular.module('superdesk.userSettings', []).
        /**
         * UserSettings service to store plugin/controller specific settings such as 
         * items per page or displayed fields.
         *
         * Usage:
         * var listSettings = userSettings('users:list', default);
         * listSettings.test = 5;
         * listSettings.save();
         *
         * Params:
         * @param {string} key - main key for accessing plugin/controller settings
         * @param {Object} defaultSettings - default settings
         */
        factory('userSettings', ['storage', function(storage) {
            var UserSettingsContainer = function(key, defaultSettings) {
                this._key = key + ':userSettings';
                _.extend(this, defaultSettings);
            };
            UserSettingsContainer.prototype.save = function() {
                var settings = {};
                for (var i in this) {
                    if (this.hasOwnProperty(i) && i !== '_key') {
                        settings[i] = this[i];
                    }
                }
                storage.setItem(this._key, settings, true);
            };
            UserSettingsContainer.prototype.load = function() {
                var settings = storage.getItem(this._key);
                if (settings !== null) {
                    for (var i in settings) {
                        if (i !== '_key') {
                            this[i] = settings[i];
                        }
                    }
                } else {
                    this.save();
                }
            };

            return function(pluginName, defaultSettings) {
                var instance = new UserSettingsContainer(pluginName, defaultSettings);
                instance.load();
                return instance;
            };
        }]);
});
