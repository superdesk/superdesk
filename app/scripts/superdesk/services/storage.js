define(['angular'], function(angular) {
    'use strict';

    angular.module('superdesk.services').
        service('storage', function() {
            this.getItem = function(key) {
                var storage = localStorage.hasOwnProperty(key) ? localStorage : sessionStorage;
                return angular.fromJson(storage.getItem(key));
            };

            this.setItem = function(key, data, remember) {
                var storage = remember ? localStorage : sessionStorage;
                return storage.setItem(key, angular.toJson(data));
            };

            this.removeItem = function(key) {
                localStorage.removeItem(key);
                sessionStorage.removeItem(key);
            };

            this.clear = function() {
                localStorage.clear();
                sessionStorage.clear();
            };
        });
});
