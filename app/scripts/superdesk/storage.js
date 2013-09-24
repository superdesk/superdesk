define(['angular'], function(angular) {
    'use strict';

    angular.module('superdesk.storage', []).
        service('storage', function() {

            var sessionStorage = window.sessionStorage || {};
            var localStorage = window.localStorage || {};

            return new function() {
                this.getItem = function(key) {
                    return angular.fromJson(sessionStorage.getItem(key));
                };

                this.setItem = function(key, data, remember) {
                    return sessionStorage.setItem(key, angular.toJson(data));
                };

                this.removeItem = function(key) {
                    localStorage.removeItem(key);
                    sessionStorage.removeItem(key);
                };

                this.clear = function() {
                    localStorage.clear();
                    sessionStorage.clear();
                };
            };
        });
});