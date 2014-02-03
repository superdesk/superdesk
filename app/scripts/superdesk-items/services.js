define(['lodash', 'angular'], function(_, angular) {
    'use strict';

    angular.module('superdesk.items.services', [])
        /**
         * Set items for further work, in next step of the workflow.
         */
        .service('workqueue', [function() {
            var queue = [];
            this.length = 0;
            this.active = null;

            /**
             * Add an item into queue
             *
             * it checks if item is in queue already and if yes it will move it to the very end
             *
             * @param {Object} item
             */
            this.add = function(item) {
                _.remove(queue, {_id: item._id});
                queue.unshift(item);
                this.length = queue.length;
                this.active = item;
                return this;
            };

            /**
             * Get first item
             */
            this.first = function() {
                return _.first(queue);
            };

            /**
             * Get all items from queue
             */
            this.all = function() {
                return queue;
            };

            /**
             * Find item by given criteria
             */
            this.find = function(criteria) {
                return _.find(queue, criteria);
            };

            /**
             * Set given item as active
             */
            this.setActive = function(item) {
                this.active = this.find({_id: item._id});
            };
        }])
        .service('panesService', ['storage', 'superdesk', function(storage, superdesk) {
            var paneKey = 'aes:panes';

            this.load = function() {
                var userPanes = storage.getItem(paneKey) || {};

                angular.forEach(superdesk.panes, function(userPane, key) {
                    userPanes[key] = angular.extend({}, userPane, userPanes[key]);
                });

                return userPanes;
            };

            this.save = function(userPanes) {
                var config = {};

                angular.forEach(userPanes, function(pane, key) {
                    config[key] = _.pick(pane, ['order', 'position', 'active', 'selected']);
                });

                storage.setItem(paneKey, config, true);
            };

            this.changePosition = function(key, position) {
                var userPanes = this.load();
                userPanes[key].position = angular.extend(userPanes[key].position, position);
                this.save(userPanes);
            };

        }]);
});
