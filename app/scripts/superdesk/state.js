define(['angular'], function(angular) {
    'use strict';

    angular.module('superdesk.state', []).
        /**
         * State service to handle application state
         *
         * Usage:
         * var currentState = state(defaultParams, currentParams);
         * currentState.set('page', 2);
         *
         * Params:
         * @param {Object} defaultParams - default parameters
         * @param {Object} currentParams - current parameters
         */
        factory('state', ['$location', function($location) {
            var StateContainer = function(defaultParams, params) {
                this.defaultParams = defaultParams;
                this.params = _.extend({}, defaultParams, params);
            };
            StateContainer.prototype.set = function(key, value) {
                this.params[key] = value;
                this._update();
            };
            StateContainer.prototype.setAll = function(params) {
                this.params = _.extend({}, params);
                this._update();
            };
            StateContainer.prototype.get = function(key) {
                return this.params[key];
            };
            StateContainer.prototype.getAll = function() {
                return this.params;
            };
            StateContainer.prototype._update = function() {
                var self = this;
                var params = {};
                _.forEach(this.params, function(value, key) {
                    if (value !== self.defaultParams[key]) {
                        params[key] = value;
                    }
                });
                $location.search(params);
            };

            return function(defaultParams, params) {
                var instance = new StateContainer(defaultParams, params);
                return instance;
            };

        }]);
});