define(['angular'], function(angular) {
    'use strict';

    angular.module('superdesk.services')
        /**
         * LocalStorage wrapper
         *
         * it stores data as json to keep its type
         */
        .service('storage', function() {

            /**
             * Get item from storage
             *
             * @param {string} key
             * @returns {mixed}
             */
            this.getItem = function(key) {
                return angular.fromJson(localStorage.getItem(key));
            };

            /**
             * Set storage item
             *
             * @param {string} key
             * @param {mixed} data
             */
            this.setItem = function(key, data) {
                localStorage.setItem(key, angular.toJson(data));
            };

            /**
             * Remove item from storage
             *
             * @param {string} key
             */
            this.removeItem = function(key) {
                localStorage.removeItem(key);
            };

            /**
             * Remove all items from storage
             */
            this.clear = function() {
                localStorage.clear();
            };
        });
});
