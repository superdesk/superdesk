define(['angular'], function(angular) {
    'use strict';

    angular.module('superdesk.storage', []).
        factory('storage', function() {

            var sessionStorage = window.sessionStorage || {};
            var localStorage = window.localStorage || {};

            return function(ns) {

                function prefixKey(key) {
                    return ns + key;
                }

                this.getItem = function(key) {
                    return angular.fromJson(sessionStorage.getItem(prefixKey(key)));
                };

                this.setItem = function(key, data) {
                    return sessionStorage.setItem(prefixKey(key), angular.toJson(data));
                };

                this.clear = function() {
                    sessionStorage.clear();
                };
            };
        });
});